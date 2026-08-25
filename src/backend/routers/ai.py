"""AI router — async quiz/test generation over the local LLM (SS-AI).

Wires /api/ai/* to services/llm_pipeline.py with background jobs whose
results reach the caller through the SSE pub/sub bus; every endpoint
degrades to 503 when AI_ENABLED is false and to SSE *_failed events on
model errors. Mounted by main.py; consumes catalog_repository,
assess_repository, llm_pipeline and events.publisher.
"""
import logging
import threading
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config import app_settings as settings
from backend.database import get_db
from backend.events import publisher
from backend.policies.auth_policy import get_current_user
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.services import llm_pipeline as pipe
from backend.services.assess_service import normalize_key

logger = logging.getLogger(__name__)
router = APIRouter()


class WizardQuizIn(BaseModel):
    """POST /api/ai/wizard-quiz body."""
    goal: str


class PracticeTestIn(BaseModel):
    """POST /api/ai/tests/generate body."""
    skill_id: int
    n_questions: int = Field(default=5, ge=1, le=20)


def _spawn(fn) -> None:
    """Run fn on a daemon thread so HTTP handlers return immediately.

    Called by generate_wizard_quiz and generate_practice_test to launch
    _wizard_job / _practice_job; tests monkeypatch this seam inline.
    """
    threading.Thread(target=fn, daemon=True).start()


def _gate() -> None:
    """Raise 503 when the AI_ENABLED flag is off.

    Callee of generate_wizard_quiz and generate_practice_test as their
    first check after authentication.
    """
    if not settings.AI_ENABLED:
        raise HTTPException(status_code=503,
                            detail="AI features are disabled")


def _seed_questions(db: Session) -> list[dict]:
    """Collect every existing question prompt as dedupe corpus entries.

    Called by generate_wizard_quiz before spawning; reads via
    assess_repository.get_all_assessments/get_questions.
    """
    out = []
    for a in arepo.get_all_assessments(db):
        out.extend({"text": q.prompt} for q in arepo.get_questions(db, a.id))
    return out


@router.post("/ai/wizard-quiz")
def generate_wizard_quiz(data: WizardQuizIn, db: Session = Depends(get_db),
                         current_user=Depends(get_current_user)):
    """Queue a role-wide adaptive diagnostic quiz; SSE delivers it.

    Called by POST /api/ai/wizard-quiz; gates, resolves the job role and
    its skills, then spawns _wizard_job and returns {"job_id": ...}.
    """
    _gate()
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        raise HTTPException(status_code=404, detail="Unknown job role")
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    if not skills:
        raise HTTPException(status_code=404, detail="Role has no skills")
    job_id = uuid.uuid4().hex
    payload = {
        "role": data.goal,
        "skills": [{"name": s.name, "difficulty": s.difficulty_level or 1}
                   for s in skills]}
    exclude = {q["text"] for q in _seed_questions(db)}
    user_id = current_user.id
    _spawn(lambda: _wizard_job(user_id, job_id, payload, exclude))
    return {"job_id": job_id}


def _wizard_job(user_id: int, job_id: str, payload: dict,
                exclude: set) -> None:
    """Generate the role quiz, convert tags to wire ids, emit SSE.

    Spawned by generate_wizard_quiz; calls pipe.generate_role_quiz,
    rebuilds ids as normalize_key(skill).lower()_q<i> with per-skill
    index restart, then publisher.send_event ai_quiz_ready/failed.
    """
    try:
        raw = pipe.generate_role_quiz(payload["role"], payload["skills"],
                                      exclude_texts=exclude)
        questions, counters = [], {}
        for q in raw:
            key = normalize_key(q["skill"]).lower()
            i = counters.get(key, 0)
            counters[key] = i + 1
            questions.append({"id": f"{key}_q{i}", "skill": q["skill"],
                              "text": q["text"], "options": q["options"]})
        publisher.send_event(user_id, "ai_quiz_ready",
                             {"job_id": job_id, "questions": questions})
    except Exception as exc:  # noqa: BLE001 — reported over SSE
        logger.warning("wizard-quiz job %s failed: %s", job_id, exc)
        publisher.send_event(user_id, "ai_quiz_failed",
                             {"job_id": job_id, "error": str(exc)[:200]})


@router.post("/ai/tests/generate")
def generate_practice_test(data: PracticeTestIn,
                           db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    """Queue a single-skill adaptive practice test; persists result.

    Called by POST /api/ai/tests/generate; gates, validates the skill,
    gathers exclusion prompts from its existing assessment, then spawns
    _practice_job and returns {"job_id": ...}.
    """
    _gate()
    skill = catalog_repository.get_skill(db, data.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Unknown skill")
    existing = arepo.get_assessments_for_skills(
        db, [skill.id]).get(skill.id)
    exclude = {q.prompt for q in
               (arepo.get_questions(db, existing.id) if existing else [])}
    job_id = uuid.uuid4().hex
    meta = {"skill_id": skill.id, "skill_name": skill.name,
            "difficulty": skill.difficulty_level or 1,
            "n": data.n_questions, "exclude": exclude}
    _spawn(lambda: _practice_job(current_user.id, job_id, meta))
    return {"job_id": job_id}


def _practice_job(user_id: int, job_id: str, meta: dict) -> None:
    """Generate, persist an [AI] assessment, emit ai_test_ready/failed.

    Spawned by generate_practice_test; opens its own SessionLocal
    session (background threads cannot reuse the request session),
    persists via assess_repository.create_assessment_with_questions and
    rolls back + closes on any failure.
    """
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        questions = pipe.generate_skill_quiz(
            meta["skill_name"], meta["difficulty"], meta["n"],
            exclude_texts=meta["exclude"])
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
