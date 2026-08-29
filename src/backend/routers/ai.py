"""AI router — instant seeded-bank quiz delivery + opt-in LLM enrichment.

Wires /api/ai/* to question_bank.py and llm_pipeline.py. The wizard quiz and
practice tests are primary-path synchronous: questions come from each skill's
seeded assessment bank and return inline — no 503 gate, no thread, no SSE
wait. The LLM runs only on enrich=true with AI enabled + engine available;
its jobs stream more=True and write AI_QUIZ_BANK so /wizard/analysis grades
the delivered questions. /ai/explain stays the sole gated LLM endpoint.
"""
import logging
import threading
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.events import publisher
from backend.policies.auth_policy import get_current_user
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.services import assess_service, question_bank, settings_service
from backend.services import llm_pipeline as pipe
from backend.services.assess_service import normalize_key

logger = logging.getLogger(__name__)
router = APIRouter()

AI_QUIZ_BANK: dict[str, dict[str, list[int]]] = {}
"""Ephemeral answer keys for AI ENRICHMENT wizard quizzes: job_id →
{normalized_skill_key.lower(): [correct_index per delivered question]}.

Seeded by opt-in enrichment jobs, not the primary delivery path (graded by
_build_report_rows/_score_answers). Enrichment pre-seeds the bank from the
delivered questions so grading works immediately, then replaces it from the
LLM output on success. Read by wizard_analysis on matching quiz_job_id.
"""

_BANK_CAP = 200


class WizardQuizIn(BaseModel):
    """POST /api/ai/wizard-quiz body."""
    goal: str
    locale: str = "en"
    enrich: bool = False


class PracticeTestIn(BaseModel):
    """POST /api/ai/tests/generate body."""
    skill_id: int
    n_questions: int = Field(default=5, ge=1, le=20)
    locale: str = "en"
    enrich: bool = False


def _spawn(fn) -> None:
    """Run fn on a daemon thread so enrichment handlers return immediately.

    Called by the two generators; tests monkeypatch this seam inline.
    """
    threading.Thread(target=fn, daemon=True).start()


def _gate() -> None:
    """Raise 503 when the AI_ENABLED flag is off; callee of explain_result
    only (sole remaining gated endpoint)."""
    if not settings_service.is_ai_enabled():
        raise HTTPException(status_code=503,
                            detail="AI features are disabled")


def _enrich_ready() -> bool:
    """True iff AI is enabled and the local engine can serve enrichment;
    called by the generators to decide whether to spawn the opt-in job."""
    from backend.services import llm_engine
    return settings_service.is_ai_enabled() and llm_engine.available()


def _seed_questions(db: Session) -> list[dict]:
    """Collect every existing question prompt as dedupe corpus entries.

    Called by generate_wizard_quiz before spawning enrichment.
    """
    out = []
    for a in arepo.get_all_assessments(db):
        out.extend({"text": q.prompt} for q in arepo.get_questions(db, a.id))
    return out


@router.get("/ai/status")
def ai_status():
    """Expose the runtime AI-enabled flag for the student wizard.

    Called by the frontend wizard; only gates optional enrichment now.
    """
    return {"ai_enabled": settings_service.is_ai_enabled()}


@router.post("/ai/wizard-quiz")
def generate_wizard_quiz(data: WizardQuizIn, db: Session = Depends(get_db),
                          current_user=Depends(get_current_user)):
    """Deliver a role quiz synchronously from the seeded bank; enrich opt-in.

    Called by POST /api/ai/wizard-quiz; returns {job_id, questions} inline.
    When enrich && _enrich_ready() spawns _wizard_job seeded with the bank
    answer keys so the LLM appends + grades.
    """
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        raise HTTPException(status_code=404, detail="Unknown job role")
    bank = question_bank.role_quiz_bank(db, data.goal)
    if not bank["questions"]:
        raise HTTPException(status_code=404, detail="Role has no quiz questions")
    job_id = uuid.uuid4().hex
    if data.enrich and _enrich_ready():
        skills = catalog_repository.get_skills_by_ids(
            db, catalog_repository.get_job_role_skill_ids(db, role.id))
        exclude = {q["text"] for q in _seed_questions(db)}
        payload = {"role": data.goal, "skills": bank["skills"]}
        _spawn(lambda: _wizard_job(
            current_user.id, job_id, payload, exclude, data.locale or "en",
            seed_keys=_bank_keys(db, skills)))
    return {"job_id": job_id, "questions": bank["questions"]}


def _bank_keys(db: Session, skills) -> dict[str, list[int]]:
    """Per-skill correct-index lists for the delivered bank questions.

    Called by generate_wizard_quiz to pre-seed the enrichment answer-key bank
    so grading works even before/without the LLM job; indexes seed questions
    in delivery order to line up with the returned bank ids.
    """
    assessments = arepo.get_assessments_for_skills(db, [s.id for s in skills])
    out: dict[str, list[int]] = {}
    for s in skills:
        a = assessments.get(s.id)
        out[normalize_key(s.name).lower()] = (
            [q.correct_index for q in arepo.get_questions(db, a.id)] if a else [])
    return out


def _wizard_job(user_id: int, job_id: str, payload: dict,
                exclude: set, locale: str = "en",
                seed_keys: dict | None = None) -> None:
    """Generate the LLM role quiz per skill, stream progress, store keys.

    Spawned by generate_wizard_quiz in enrich mode only. Pre-seeds
    AI_QUIZ_BANK[job_id] from seed_keys so /wizard/analysis grades the bank
    questions even before the LLM finishes; pipes the role quiz (on_skill
    emitting more=True, ids <key>_q<i> for UX) and on success replaces the
    bank from the LLM output + sends final more=False. On failure with
    seed_keys the seeded bank stays (soft); otherwise ai_quiz_failed fires.
    """
    if seed_keys is not None:
        AI_QUIZ_BANK[job_id] = dict(seed_keys)
        while len(AI_QUIZ_BANK) > _BANK_CAP:
            AI_QUIZ_BANK.pop(next(iter(AI_QUIZ_BANK)))
    counters: dict[str, int] = {}

    def _on_skill(name: str, chunk: list[dict]) -> None:
        key = normalize_key(name).lower()
        delta: list[dict] = []
        for q in chunk:
            i = counters.get(key, 0)
            counters[key] = i + 1
            delta.append({"id": f"{key}_q{i}", "skill": name,
                          "text": q["text"], "options": q["options"]})
        publisher.send_event(user_id, "ai_quiz_ready",
                              {"job_id": job_id, "questions": delta,
                               "more": True})

    try:
        raw = pipe.generate_role_quiz(
            payload["role"], payload["skills"], exclude_texts=exclude,
            locale=locale, on_skill=_on_skill)
        if not raw:
            raise RuntimeError("no questions generated for any skill")
        keys: dict[str, list[int]] = {}
        for q in raw:
            key = normalize_key(q["skill"]).lower()
            keys.setdefault(key, []).append(q["correct_index"])
        AI_QUIZ_BANK[job_id] = keys
        while len(AI_QUIZ_BANK) > _BANK_CAP:
            AI_QUIZ_BANK.pop(next(iter(AI_QUIZ_BANK)))
        publisher.send_event(user_id, "ai_quiz_ready",
                              {"job_id": job_id, "questions": [],
                               "more": False})
    except Exception as exc:  # noqa: BLE001 — reported over SSE
        logger.warning("wizard-quiz job %s failed: %s", job_id, exc)
        if seed_keys is None:
            publisher.send_event(user_id, "ai_quiz_failed",
                                  {"job_id": job_id, "error": str(exc)[:200]})


@router.post("/ai/tests/generate")
def generate_practice_test(data: PracticeTestIn,
                           db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    """Deliver a single-skill practice quiz synchronously; persist on enrich.

    Called by POST /api/ai/tests/generate; reads the seeded bank and returns
    {job_id, assessment_id, skill_id, questions} inline for QuizRunner use
    (submitted via /assessments/submit). When enrich && _enrich_ready() also
    spawns the persisted [AI] adaptive-assessment job.
    """
    bank = question_bank.skill_quiz_bank(db, data.skill_id)
    if not bank["skill"]:
        raise HTTPException(status_code=404, detail="Unknown skill")
    job_id = uuid.uuid4().hex
    if data.enrich and _enrich_ready():
        skill = catalog_repository.get_skill(db, data.skill_id)
        existing = arepo.get_assessments_for_skills(
            db, [skill.id]).get(skill.id)
        exclude = {q.prompt for q in
                   (arepo.get_questions(db, existing.id) if existing else [])}
        meta = {"skill_id": skill.id, "skill_name": skill.name,
                "difficulty": skill.difficulty_level or 1,
                "n": data.n_questions, "exclude": exclude,
                "locale": data.locale or "en"}
        _spawn(lambda: _practice_job(current_user.id, job_id, meta))
    return {"job_id": job_id, "assessment_id": bank["assessment_id"],
            "skill_id": bank["skill_id"], "skill": bank["skill"],
            "questions": bank["questions"]}


def _practice_job(user_id: int, job_id: str, meta: dict) -> None:
    """Generate, persist an [AI] assessment, emit ai_test_ready/failed.

    Spawned by generate_practice_test in enrich mode; opens its own
    SessionLocal session (background threads cannot reuse the request one),
    persists via create_assessment_with_questions, rolls back + closes on any
    failure.
    """
    from backend.database import SessionLocal
    from backend.entities.learning import UserSkill
    db = SessionLocal()
    try:
        skill = catalog_repository.get_skill(db, meta["skill_id"])
        topics = skill.topics if skill and skill.topics else None
        us = db.query(UserSkill).filter_by(
            user_id=user_id, skill_id=meta["skill_id"]).first()
        proficiency_level = us.proficiency_level if us else None
        questions = pipe.generate_skill_quiz(
            meta["skill_name"], meta["difficulty"], meta["n"],
            exclude_texts=meta["exclude"],
            proficiency_level=proficiency_level,
            topics=topics, locale=meta.get("locale", "en"))
        assessment = arepo.create_assessment_with_questions(
            db, meta["skill_id"], f"[AI] {meta['skill_name']} — adaptive",
            "Generated by SS-AI from weakness analysis", 60, questions)
        publisher.send_event(user_id, "ai_test_ready",
                             {"job_id": job_id, "assessment_id": assessment.id,
                              "skill_id": meta["skill_id"]})
    except Exception as exc:  # noqa: BLE001 — reported over SSE
        db.rollback()
        logger.warning("practice job %s failed: %s", job_id, exc)
        publisher.send_event(user_id, "ai_test_failed",
                             {"job_id": job_id, "error": str(exc)[:200]})
    finally:
        db.close()


class ExplainIn(BaseModel):
    """POST /api/ai/explain body — answers re-supplied because the
    reduced schema stores scores, not selected indices."""
    assessment_id: int
    answers: List[int] = []


@router.post("/ai/explain")
def explain_result(data: ExplainIn, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    """Sync per-question explanations + advice (static fallback).

    Called by POST /api/ai/explain; gates 503 via _gate (sole gated LLM
    endpoint), validates IDs, grades via assess_service._grade.
    """
    _gate()
    assessment = arepo.get_assessment(db, data.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    questions = arepo.get_questions(db, assessment.id)
    if not questions:
        raise HTTPException(status_code=400, detail="No questions")
    _, _, responses = assess_service._grade(questions, data.answers)
    narrative = pipe.explain_result(responses)
    if narrative:
        return {**narrative, "narrative_available": True}
    return {
        "explanations": [{"question_index": r["question_index"],
                          "why": f"Correct answer: "
                                 f"{r['correct_answer']}"}
                         for r in responses],
        "advice": "", "narrative_available": False}
