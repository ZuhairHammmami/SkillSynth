"""Step test service — generate + grade targeted step tests (Phase 2D/2E).

Given a path step, builds a small (3-5) MCQ on its skill, sourced by default
from the skill's seeded assessment bank (deterministic, instant, no LLM on
the request path). AI topic/quiz enrichment and the post-grade bounded
proficiency review run on daemon threads via step_jobs (SSE ai_step_quiz_ready,
proficiency_adjusted, ai_step_diagnostic). Grading updates user_skills
weak_points + proficiency_level deterministically and completes the step on
pass. Reuses assess_repository, catalog_repository, learning_repository and
learning_service.complete_step — no duplicated logic. Pure math lives in
step_test_engine.py and AI jobs in step_jobs.py (300-line limit).
"""

from __future__ import annotations

import threading

from sqlalchemy.orm import Session

from backend.entities.learning import UserSkill
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.repositories import learning_repository as lrepo
from backend.services import learning_service
from backend.services import settings_service, step_jobs, step_test_engine
from backend.services.step_test_engine import (
    MASTERY_SCALE, _PASS_THRESHOLD, _assemble_grade_result,
    _assemble_payload, _decorate_questions, _score_answers,
    _select_topics, _topics_for, compute_effective_difficulty,
)


def _step_context(db: Session, user_id: int, step_id: int):
    """Resolve step + owning path + skill; (ctx, error, status)."""
    step = lrepo.get_step(db, step_id)
    if not step:
        return None, "Step not found", 404
    path = lrepo.get_path(db, step.path_id, user_id)
    if not path:
        return None, "Path not found", 404
    skill = (catalog_repository.get_skill(db, step.skill_id)
             if step.skill_id else None)
    if not skill:
        return None, "Step has no skill to test", 400
    return {"step": step, "path": path, "skill": skill}, None, None


def _proficiency(db: Session, user_id: int, skill_id: int) -> int:
    """Current proficiency_level for the skill, default 0."""
    us = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill_id).first()
    return us.proficiency_level if us else 0


def _recent_outcome(db: Session, user_id: int):
    """Most recent assessment attempt outcome as {"passed": bool} or None."""
    results = arepo.results_for_user(db, user_id)
    if not results:
        return None
    return {"passed": bool(results[-1].passed)}


def _seeded_questions(db: Session, skill) -> list[dict]:
    """First 3..5 questions of the skill's first seeded assessment."""
    assessment = arepo.get_assessments_for_skills(
        db, [skill.id]).get(skill.id)
    if not assessment:
        return []
    qs = arepo.get_questions(db, assessment.id)
    if not qs:
        return []
    out = [{
        "id": q.id, "text": q.prompt, "options": list(q.options),
        "correct_index": q.correct_index, "assessment_id": assessment.id,
    } for q in qs[:5]]
    return out


def _spawn(fn) -> None:
    """Run fn on a daemon thread (seam; tests run it inline)."""
    threading.Thread(target=fn, daemon=True).start()


def _spawn_review(fn) -> None:
    """Run a bounded review on a daemon thread (seam; tests run it inline)."""
    _spawn(fn)


def _engine_ready() -> bool:
    """Guard indirection for llm_engine.available (tests monkeypatch)."""
    from backend.services import llm_engine
    return llm_engine.available()


def _ai_available(ai_enabled) -> bool:
    """True when AI is on for step tests: explicit flag AND a ready engine.

    Callee of generate_step_test; ai_enabled (explicit) wins over the
    runtime settings flag (mirrors the old _ai_active behavior).
    """
    enabled = ai_enabled if ai_enabled is not None \
        else settings_service.is_ai_enabled()
    return bool(enabled) and _engine_ready()


def _ai_active() -> bool:
    """AI gate for step tests follows the runtime settings store + engine.

    Seam kept for test_ai_flag_unification; delegates to _ai_available with
    no explicit flag so it reads settings_service.is_ai_enabled().
    """
    return _ai_available(None)


def generate_step_test(db: Session, user_id: int, step_id: int,
                       locale: str = "en", level: int = None,
                       ai_enabled: bool = None, enrich: bool = False):
    """Build the synchronous step-test payload from the seeded bank.

    Caller: paths.step_test. Callee: _step_context, _select_topics,
    _proficiency, _recent_outcome, compute_effective_difficulty,
    _seeded_questions, _decorate_questions, _assemble_payload. Never calls
    the LLM on the request path; when enrich && AI ready spawns
    step_jobs.ai_enrich_job (SSE ai_step_quiz_ready). Returns
    (payload|None, error|None, status).
    """
    ctx, err, status = _step_context(db, user_id, step_id)
    if err:
        return None, err, status
    skill, step = ctx["skill"], ctx["step"]
    eff_level = level if level is not None else (step.current_level or 1)
    topics = _select_topics(skill, step, eff_level)
    proficiency = _proficiency(db, user_id, skill.id)
    user_skill = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    last = _recent_outcome(db, user_id)
    difficulty = compute_effective_difficulty(skill, user_skill, topics, last)
    questions = _seeded_questions(db, skill)
    if not questions:
        return None, "No questions available for this skill", 400
    assessment_id = questions[0]["assessment_id"]
    payload = _assemble_payload(
        step_id, skill, difficulty, topics, assessment_id,
        _decorate_questions(questions, topics))
    if enrich and _ai_available(ai_enabled):
        _spawn(lambda: step_jobs.ai_enrich_job(
            user_id, step_id, skill.id, skill.name, difficulty,
            proficiency, topics, locale))
    return payload, None, None


def _persist_level(db, user_id, skill, weak_points, correct, total) -> int:
    """Persist the deterministic formula level + merged weak points.

    Caller: _grade. Callee: arepo.upsert_user_skill. next_level is the
    clamp(0..5, round(correct/total*5)) formula (no LLM); commits in the
    caller's session.
    """
    next_level = max(0, min(MASTERY_SCALE,
                            round(correct / total * MASTERY_SCALE)))
    arepo.upsert_user_skill(db, user_id, skill.id, next_level)
    db.flush()
    us = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    merged = list(us.weak_points or [])
    for t in weak_points:
        if t not in merged:
            merged.append(t)
    us.weak_points = merged
    db.commit()
    return next_level


def _resources_for(db, step) -> list[dict]:
    """Resolve step resources to lightweight dicts; [] when none."""
    return [{
        "id": r.id, "title": r.title, "url": r.url, "type": r.type}
        for r in catalog_repository.get_resources_by_ids(
            db, step.resource_ids or [])]


def _queue_review(user_id, skill_id, correct, total, next_level,
                  difficulty, attempt_no, topics, locale):
    """Spawn the bounded post-submit review off the request path.

    Caller: _grade after its commit; callee: step_jobs.review_and_adjust via
    _spawn_review. Hands the reviewer the deterministic next_level and the
    attempt number for its ±1 bounded-autonomy verdict.
    """
    _spawn_review(lambda: step_jobs.review_and_adjust(
        user_id, skill_id, correct, total, difficulty, attempt_no,
        next_level, topics, locale))


def _grade(db: Session, user_id: int, ctx, data, locale: str):
    """Grade answers deterministically; persist, complete step, review async.

    Caller: grade_step_test. Callee: _score_answers, compute_effective_difficulty,
    _persist_level, learning_service.complete_step, _resources_for,
    _assemble_grade_result, _queue_review.
    """
    skill, step = ctx["skill"], ctx["step"]
    topics = _topics_for(skill, step)
    answers = data.get("answers") or {}
    if not answers:
        return None, "No answers submitted", 400
    assessment_id = data.get("assessment_id")
    qs = arepo.get_questions(db, assessment_id) if assessment_id else []
    scored = _score_answers(answers, qs, topics)
    if scored is None:
        return None, "No valid answers", 400
    total, correct, weak_points, topics_to_master, graded, score, passed = scored
    user_skill = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    current_level = user_skill.proficiency_level if user_skill else 0
    difficulty = compute_effective_difficulty(skill, user_skill, topics)
    next_level = _persist_level(
        db, user_id, skill, weak_points, correct, total)
    completed = bool(passed)
    if passed:
        learning_service.complete_step(db, user_id, ctx["step"].id)
    resources = _resources_for(db, step)
    result = _assemble_grade_result(
        passed, score, correct, total, weak_points, topics_to_master,
        resources, completed, next_level, current_level, assessment_id,
        graded)
    if settings_service.is_ai_enabled() and _engine_ready():
        attempt_no = len(arepo.results_for_user(db, user_id))
        _queue_review(user_id, skill.id, correct, total, next_level,
                      difficulty, attempt_no, topics, locale)
    return result, None, None


def grade_step_test(db: Session, user_id: int, step_id: int, data: dict,
                    locale: str = "en"):
    """Entry point: resolve context then grade; (result, error, status)."""
    ctx, err, status = _step_context(db, user_id, step_id)
    if err:
        return None, err, status
    return _grade(db, user_id, ctx, data, locale)
