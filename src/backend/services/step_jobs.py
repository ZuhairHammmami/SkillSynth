"""Background AI jobs for step tests (bank-first request path + async AI).

The step-test request path stays deterministic and instant; these jobs run
on daemon threads spawned by step_test_service (_spawn/_spawn_review), each
opening its OWN SessionLocal because background threads cannot reuse the
request session. db.close() in finally. Mirrors
assess_service._review_and_adjust and routers/ai._practice_job.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def ai_enrich_job(user_id: int, step_id: int, skill_id: int,
                  skill_name: str, difficulty: int, proficiency: int,
                  topics: list, locale: str) -> None:
    """Generate an [AI] step quiz and stream ai_step_quiz_ready over SSE.

    Spawned by step_test_service.generate_step_test (enrich=true only);
    opens its own SessionLocal, persists the AI assessment via
    create_assessment_with_questions, and emits ai_step_quiz_ready carrying
    the assessment_id the learner can submit against.
    """
    from backend.database import SessionLocal
    from backend.events.publisher import send_event
    from backend.repositories import assess_repository as arepo
    from backend.services import llm_pipeline
    db = SessionLocal()
    try:
        raw = llm_pipeline.generate_skill_quiz(
            skill_name, difficulty=difficulty, n=4,
            proficiency_level=proficiency, topics=topics or None,
            locale=locale)
        assessment = arepo.create_assessment_with_questions(
            db, skill_id, f"[AI] {skill_name} — step {step_id} test",
            "Targeted step completion test", 60, raw)
        send_event(user_id, "ai_step_quiz_ready",
                   {"assessment_id": assessment.id, "skill_id": skill_id,
                    "step_id": step_id})
    except Exception as exc:  # noqa: BLE001 — reported over SSE
        db.rollback()
        logger.warning("step enrich job %s failed: %s", step_id, exc)
        send_event(user_id, "ai_quiz_failed",
                   {"step_id": step_id, "error": str(exc)[:200]})
    finally:
        db.close()


def _apply_adjustment(db, user_id: int, skill_id: int, verdict: dict) -> None:
    """Persist user_skills, audit + step ladder, emit proficiency_adjusted SSE.

    Callee of review_and_adjust on an applied (bounded ±1) verdict; writes the
    ai_proficiency_review audit row and syncs the caller's step current_level.
    """
    from backend.events.publisher import send_admin_activity, send_event
    from backend.repositories import (
        assess_repository as arepo, engagement_repository,
        learning_repository as lrepo,
    )
    arepo.upsert_user_skill(db, user_id, skill_id, verdict["final_level"])
    db.commit()
    row = engagement_repository.write(
        db, "audit", "ai_proficiency_review", user_id=user_id,
        entity_type="skill", entity_id=skill_id,
        data={"delta": verdict["delta"], "rationale": verdict["rationale"],
              "final_level": verdict["final_level"]})
    send_admin_activity(row)
    lrepo.update_step_current_level_for_skill(
        db, user_id, skill_id, verdict["final_level"])
    send_event(user_id, "proficiency_adjusted",
               {"skill_id": skill_id, "delta": verdict["delta"],
                "rationale": verdict["rationale"]})


def review_and_adjust(user_id: int, skill_id: int, correct: int, total: int,
                      difficulty: int, attempt_no: int, level_now: int,
                      topics: list, locale: str) -> None:
    """Own-session reviewer: ladder sync + audit + diagnostic SSE.

    Spawned by step_test_service._queue_review after a deterministic grade.
    Delegates the verdict to assess_service.review_level; on applied verdicts
    calls _apply_adjustment (user_skills + step ladder + audit +
    proficiency_adjusted SSE, bounded ±1 per ADR-015), then runs
    analyze_diagnostic and emits ai_step_diagnostic SSE. On failure rolls
    back and emits proficiency_review_failed SSE.
    """
    from backend.database import SessionLocal
    from backend.events.publisher import send_event
    from backend.services import assess_service
    db = SessionLocal()
    try:
        verdict = assess_service.review_level(
            correct, total, difficulty, attempt_no, level_now)
        if verdict.get("applied"):
            _apply_adjustment(db, user_id, skill_id, verdict)
        _emit_diagnostic(db, user_id, skill_id, correct, total, level_now,
                         topics, locale)
    except Exception as exc:  # noqa: BLE001 — reported over SSE
        db.rollback()
        logger.warning("step review job failed: %s", exc)
        send_event(user_id, "proficiency_review_failed",
                   {"skill_id": skill_id, "error": str(exc)[:200]})
    finally:
        db.close()


def _emit_diagnostic(db, user_id: int, skill_id: int, correct: int,
                     total: int, level_now: int, topics: list,
                     locale: str) -> None:
    """Emit ai_step_diagnostic SSE with refined weak points, if narrative."""
    from backend.events.publisher import send_event
    from backend.repositories import catalog_repository
    from backend.services import learning_service, llm_pipeline
    skill = catalog_repository.get_skill(db, skill_id)
    if not skill:
        return
    per_skill = [{"skill": skill.name, "correct": correct, "total": total,
                  "assessed_level": level_now,
                  "gap": max(0, learning_service.MASTERY_LEVEL - level_now)}]
    narrative = llm_pipeline.analyze_diagnostic(
        per_skill, topics=topics, locale=locale)
    if not narrative:
        return
    weak = list(dict.fromkeys(
        w.get("focus") for w in narrative.get("weaknesses", [])
        if w.get("focus")))
    master = list(dict.fromkeys(
        weak + [str(x) for x in narrative.get("recommended_focus", [])]))
    send_event(user_id, "ai_step_diagnostic",
               {"skill_id": skill_id, "weak_points": weak,
                "topics_to_master": master})
