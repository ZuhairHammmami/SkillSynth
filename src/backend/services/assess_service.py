"""Assessment service — question payloads and scored submissions.

Called by the assessments routers (Task 3) and routers/ai.py (explain).
Questions come from the normalized assessment_questions table;
submissions grade against correct_index, persist an AssessmentResult,
upsert user_skills and — when SS-AI is enabled and the engine is ready —
spawn a bounded proficiency-review thread (review_level seam).
"""
import threading

from backend.config import app_settings as settings
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.repositories import engagement_repository
from backend.services import llm_pipeline
from backend.services import settings_service

MASTERY_SCALE = 5


def normalize_key(name: str) -> str:
    """Skill-name → question-id key ("Machine Learning"→"machine_learning").

    Single source of truth: assess_service builds ids with it and
    learning_service._score_answers looks answers up with it, so both
    sides of the wizard round-trip stay in lockstep.
    """
    return (name.replace(" ", "_").replace("/", "_").replace("-", "_")
            .replace("(", "").replace(")", ""))


def questions_for_skill(db, job_role_title: str) -> list[dict]:
    """Question payload for GET /assessments/{job_role_title}.

    Shape is frozen: [{id: "<skill>_q<i>", skill, text, options}] —
    ids stay strings so wizard answer keys keep round-tripping into
    learning_service._score_answers.
    """
    role = catalog_repository.get_job_role_by_title(db, job_role_title)
    if not role:
        return []
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    assessments = arepo.get_assessments_for_skills(db, [s.id for s in skills])
    questions: list[dict] = []
    for skill in skills:
        assessment = assessments.get(skill.id)
        if not assessment:
            continue
        for i, q in enumerate(arepo.get_questions(db, assessment.id)):
            questions.append({
                "id": f"{normalize_key(skill.name).lower()}_q{i}",
                "skill": skill.name,
                "text": q.prompt,
                "options": q.options or [],
            })
    return questions


def _grade(questions: list, answers: list[int]) -> tuple[int, int, list]:
    """Score answers against correct_index; returns total/correct/detail.

    Detail rows keep the historical response keys (question_index,
    selected_index, is_correct, correct_answer) so result payloads and
    SSE notifications remain wire-compatible.
    """
    total = len(questions)
    correct = 0
    responses = []
    for i, q in enumerate(questions):
        selected = answers[i] if i < len(answers) else -1
        is_correct = selected == q.correct_index
        correct += 1 if is_correct else 0
        responses.append({
            "question_index": i, "question": q.prompt,
            "selected_index": selected, "is_correct": is_correct,
            "correct_answer": (q.options or [])[q.correct_index]
            if 0 <= q.correct_index < len(q.options or []) else None,
        })
    return total, correct, responses


def _serialize_result(result, total: int, responses: list) -> dict:
    """Result payload preserving legacy keys; profile_id mirrors user_id
    and submitted_at aliases completed_at for frontend compatibility."""
    return {
        "id": result.id, "profile_id": result.user_id,
        "assessment_id": result.assessment_id, "score": result.score,
        "passed": result.passed, "total_questions": total,
        "responses": responses,
        "submitted_at": result.completed_at.isoformat()
        if result.completed_at else None,
    }


def submit_result(db, user, input_data) -> tuple[dict | None, str | None, int]:
    """Grade POST /assessment-results; persists result + proficiency.

    passed = score >= pass_score; proficiency = round(correct/total*5)
    clamped to 0..5 with last_assessed_at stamped. When the skill is set
    and AI is enabled + engine ready, queues a bounded review via
    _queue_review. Returns (payload|None, error|None, http_status).
    """
    assessment = arepo.get_assessment(db, input_data.assessment_id)
    if not assessment:
        return None, "Assessment not found", 404
    questions = arepo.get_questions(db, assessment.id)
    if not questions:
        return None, "Assessment has no questions", 400
    total, correct, responses = _grade(questions, input_data.answers)
    score = round((correct / total) * 100) if total > 0 else 0
    result = arepo.create_result(
        db, user.id, assessment.id, score, score >= (assessment.pass_score or 60))
    if assessment.skill_id:
        level = max(0, min(MASTERY_SCALE,
                           round(correct / total * MASTERY_SCALE)))
        arepo.upsert_user_skill(db, user.id, assessment.skill_id, level)
        db.commit()
        if settings_service.is_ai_enabled() and _engine_ready():
            skill = catalog_repository.get_skill(db, assessment.skill_id)
            _queue_review(user.id, assessment.skill_id, correct, total,
                          result.id, skill.difficulty_level or 1,
                          attempt_no=len(arepo.results_for_user(db, user.id)))
    return _serialize_result(result, total, responses), None, 200


def review_level(correct, total, difficulty, attempt_no, current_level):
    """Thin delegate to llm_pipeline.review_level (seam for tests).

    Called by _review_and_adjust inside the reviewer thread; tests
    monkeypatch this name on assess_service to bypass the model.
    """
    return llm_pipeline.review_level(correct, total, difficulty,
                                     attempt_no, current_level)


def _spawn_review(fn):
    """Run the reviewer on a daemon thread (seam; tests run inline).

    Called by _queue_review only.
    """
    threading.Thread(target=fn, daemon=True).start()


def _engine_ready() -> bool:
    """Guard indirection for llm_engine.available (tests monkeypatch).

    Called by submit_result beside settings.AI_ENABLED; imports the
    engine lazily so non-AI installs never load inference dependencies.
    """
    from backend.services import llm_engine
    return llm_engine.available()


def _queue_review(user_id, skill_id, correct, total, result_id,
                  difficulty, attempt_no):
    """Spawn the bounded post-submit review off the request path.

    Callee of submit_result after its commit; recomputes the formula
    level and hands _review_and_adjust to _spawn_review.
    """
    level_now = max(0, min(MASTERY_SCALE,
                           round(correct / total * MASTERY_SCALE)))
    _spawn_review(lambda: _review_and_adjust(
        user_id, skill_id, correct, total, result_id, difficulty,
        attempt_no, level_now))


def _review_and_adjust(user_id, skill_id, correct, total, result_id,
                       difficulty, attempt_no, level_now):
    """Own-session reviewer: adjust level, audit, notify.

    Spawned by _queue_review; delegates the verdict to review_level and,
    on applied verdicts only, upserts user_skills in its own session,
    writes the ai_proficiency_review activity row and emits
    proficiency_adjusted SSE; otherwise returns silently.
    """
    from backend.database import SessionLocal
    from backend.events.publisher import send_admin_activity, send_event
    verdict = review_level(correct, total, difficulty, attempt_no,
                           level_now)
    if not verdict["applied"]:
        return
    db = SessionLocal()
    try:
        arepo.upsert_user_skill(db, user_id, skill_id,
                                verdict["final_level"])
        db.commit()
        row = engagement_repository.write(
            db, "audit", "ai_proficiency_review", user_id=user_id,
            entity_type="skill", entity_id=skill_id,
            data={"delta": verdict["delta"],
                  "rationale": verdict["rationale"],
                  "result_id": result_id,
                  "final_level": verdict["final_level"]})
        send_admin_activity(row)
        skill = catalog_repository.get_skill(db, skill_id)
        send_event(user_id, "proficiency_adjusted",
                   {"skill_id": skill_id,
                    "skill_name": skill.name if skill else None,
                    "delta": verdict["delta"],
                    "rationale": verdict["rationale"]})
    finally:
        db.close()


def get_assessment_by_id(db, assessment_id: int):
    """Pass-through lookup used by routers after submission."""
    return arepo.get_assessment(db, assessment_id)
