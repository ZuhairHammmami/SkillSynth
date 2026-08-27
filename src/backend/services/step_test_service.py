"""Step test service — generate + grade targeted step tests (Phase 2D/2E).

Given a path step, builds a small (3-5) MCQ on its skill, calibrated to the
learner's proficiency_level and focused on skills.topics /
path_steps.learning_objectives. AI generation (when enabled) falls back to
the skill's seeded assessment_questions. Grading updates
user_skills.weak_points + proficiency_level, and completes the step on pass.
Reuses llm_pipeline, assess_repository, catalog_repository, learning_repository
and learning_service.complete_step — no duplicated logic.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from backend.config import app_settings as settings
from backend.entities.learning import UserSkill
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.repositories import learning_repository as lrepo
from backend.services import assess_service, llm_pipeline, learning_service
from backend.services import settings_service

_PASS_THRESHOLD = 0.6
_AI_N = 4


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


def _topics_for(skill, step) -> list[str]:
    """Topic list = skill.topics, else step.learning_objectives, else [skill]."""
    topics: list[str] = []
    if skill.topics:
        topics = [str(x) for x in skill.topics if str(x).strip()]
    if not topics and step.learning_objectives:
        topics = [str(x) for x in step.learning_objectives if str(x).strip()]
    if not topics:
        topics = [skill.name]
    seen, out = set(), []
    for x in topics:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def compute_effective_difficulty(skill, user_skill, topics,
                                 last_result=None) -> int:
    """Effective quiz difficulty for a step test, tuned by recent outcome.

    Base difficulty rises by up to +2 for mastered topics (not in weak_points)
    so the local AI writes harder questions as topics are cleared, clamped
    1..5. last_result (optional) adapts to the most recent attempt: a failed
    attempt (dict {"passed": False} or False) lowers difficulty by 1 (floor 1);
    a passed attempt ({"passed": True} or True) raises it by 1 (cap 5).
    Deterministic; callers pass the prior outcome to tune the next test.
    """
    base = int(skill.difficulty_level or 1)
    weak = set(user_skill.weak_points or []) if user_skill else set()
    mastered = [t for t in topics if t and t not in weak]
    level = min(5, base + min(2, len(mastered)))
    if last_result is not None:
        passed = (last_result.get("passed")
                  if isinstance(last_result, dict) else bool(last_result))
        level = level - 1 if not passed else level + 1
    return max(1, min(5, level))


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


def _ai_active() -> bool:
    """Gate AI features for step tests; config flag AND a ready engine."""
    return bool(settings_service.is_ai_enabled()) and llm_pipeline._engine_available()


def _leveled_topics(skill_name: str, level: int) -> list[str]:
    """Topics for a leveled step test; AI when active, else seeded fallback.

    Callee of _select_topics; calls llm_pipeline.generate_skill_topics and, on
    an unavailable engine or LLM failure, delegates to the seeded deterministic
    fallback so tests stay reproducible without the LLM.
    """
    if _ai_active():
        try:
            return llm_pipeline.generate_skill_topics(skill_name, level)
        except llm_pipeline.LLMOperationError:
            pass
    count = min(3, level + 1)
    return [f"Topic {i} for {skill_name} (level {level})"
            for i in range(1, count + 1)]


def _select_topics(skill, step, eff_level) -> list[str]:
    """Leveled topics when eff_level>1, else skill/step objectives."""
    if eff_level > 1:
        return _leveled_topics(skill.name, eff_level)
    return _topics_for(skill, step)


def _ai_questions(db, skill, step_id, topics, difficulty, proficiency,
                  locale) -> tuple[list[dict], Optional[int]]:
    """Generate an AI step-test quiz; ([], None) on engine error."""
    try:
        raw = llm_pipeline.generate_skill_quiz(
            skill.name, difficulty=difficulty, n=max(_AI_N, len(topics)),
            proficiency_level=proficiency, topics=topics or None,
            locale=locale)
        assessment = arepo.create_assessment_with_questions(
            db, skill.id, f"[AI] {skill.name} — step {step_id} test",
            "Targeted step completion test", 60, raw)
        qs = arepo.get_questions(db, assessment.id)
        questions = [{
            "id": q.id, "text": q.prompt, "options": list(q.options),
            "correct_index": q.correct_index} for q in qs]
        return questions, assessment.id
    except llm_pipeline.LLMOperationError:
        return [], None


def _build_questions(db, skill, step_id, topics, difficulty, proficiency,
                     ai, locale) -> tuple[Optional[list[dict]], Optional[int]]:
    """Build (questions, assessment_id); (None, None) when no source exists.

    Tries the AI quiz when active, then the seeded bank; decorates each
    question with its topic and drops the internal assessment_id key.
    """
    questions, assessment_id = [], None
    if ai:
        questions, assessment_id = _ai_questions(
            db, skill, step_id, topics, difficulty, proficiency, locale)
    if not questions:
        seeded = _seeded_questions(db, skill)
        if not seeded:
            return None, None
        questions = seeded
        assessment_id = seeded[0]["assessment_id"]
    for i, q in enumerate(questions):
        q["topic"] = topics[i % len(topics)] if topics else None
        q.pop("assessment_id", None)
    return questions, assessment_id


def _assemble_payload(step_id, skill, difficulty, topics, assessment_id,
                      questions) -> dict:
    """Pack the step-test payload dict from computed pieces."""
    return {
        "step_id": step_id,
        "skill": {"id": skill.id, "name": skill.name,
                  "difficulty_level": skill.difficulty_level,
                  "effective_difficulty": difficulty},
        "topics": topics,
        "assessment_id": assessment_id,
        "questions": questions,
    }


def generate_step_test(db: Session, user_id: int, step_id: int,
                       locale: str = "en", level: int = None,
                       ai_enabled: bool = None):
    """Build the synchronous step test payload; (payload, error, status).

    Resolves context, selects topics (leveled or skill/step objectives),
    builds questions (AI or seeded), and returns the assembled payload.
    """
    ctx, err, status = _step_context(db, user_id, step_id)
    if err:
        return None, err, status
    skill, step = ctx["skill"], ctx["step"]
    eff_level = level if level is not None else (step.current_level or 1)
    ai = ai_enabled if ai_enabled is not None else _ai_active()
    topics = _select_topics(skill, step, eff_level)
    proficiency = _proficiency(db, user_id, skill.id)
    user_skill = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    last = _recent_outcome(db, user_id)
    difficulty = compute_effective_difficulty(skill, user_skill, topics, last)
    questions, assessment_id = _build_questions(
        db, skill, step_id, topics, difficulty, proficiency, ai, locale)
    if questions is None:
        return None, "No questions available for this skill", 400
    payload = _assemble_payload(
        step_id, skill, difficulty, topics, assessment_id, questions)
    return payload, None, None


def _score_answers(answers, qs, topics):
    """Grade answers; (total, correct, weak, master, graded, score, passed).

    Iterates the answer map against question rows, tallying correct and weak
    topics; returns the totals, the per-question graded list, and the pass
    flag (score >= _PASS_THRESHOLD). Returns None when no valid answer exists.
    """
    topic_by_id = {q.id: (topics[i % len(topics)] if topics else None)
                   for i, q in enumerate(qs)}
    rows = {q.id: q for q in qs}
    total = correct = 0
    weak: list[str] = []
    graded: list[dict] = []
    for qid_s, sel in answers.items():
        try:
            qid = int(qid_s)
        except (TypeError, ValueError):
            continue
        q = rows.get(qid)
        if not q:
            continue
        total += 1
        is_correct = sel == q.correct_index
        correct += 1 if is_correct else 0
        if not is_correct:
            tp = topic_by_id.get(qid)
            if tp and tp not in weak:
                weak.append(tp)
        graded.append({"question_id": qid, "correct": is_correct,
                       "selected": sel, "correct_index": q.correct_index})
    if total == 0:
        return None
    score = correct / total
    weak_points = list(dict.fromkeys(weak))
    remaining = [t for t in topics if t not in weak_points] if topics else []
    topics_to_master = weak_points + remaining
    return total, correct, weak_points, topics_to_master, graded, score, \
        score >= _PASS_THRESHOLD


def _persist_grade(db, user_id, skill, weak_points, correct, total,
                   difficulty, current_level) -> int:
    """Apply review_level verdict and persist proficiency + weak points.

    Returns next_level from assess_service.review_level; merges weak points
    into the user_skill row and commits within the caller's session.
    """
    us = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    if not us:
        us = UserSkill(user_id=user_id, skill_id=skill.id,
                       proficiency_level=current_level)
        db.add(us)
    attempt_no = len(arepo.results_for_user(db, user_id))
    verdict = assess_service.review_level(
        correct, total, difficulty, attempt_no, current_level)
    next_level = verdict["final_level"]
    us.proficiency_level = next_level
    merged = list(us.weak_points or [])
    for t in weak_points:
        if t not in merged:
            merged.append(t)
    us.weak_points = merged
    db.commit()
    return next_level


def _diagnostic_for_fail(db, skill, topics, correct, total, next_level,
                         locale) -> tuple[Optional[list[str]], Optional[list[str]]]:
    """Enrich weak points + focus on a failing AI-enabled grade.

    Calls llm_pipeline.analyze_diagnostic and returns updated (weak_points,
    topics_to_master); returns (None, None) when AI is inactive or empty.
    """
    per_skill = [{
        "skill": skill.name, "correct": correct, "total": total,
        "assessed_level": next_level,
        "gap": max(0, learning_service.MASTERY_LEVEL - next_level)}]
    narrative = llm_pipeline.analyze_diagnostic(
        per_skill, topics=topics, locale=locale)
    if not narrative:
        return None, None
    nw = [w.get("focus") for w in narrative.get("weaknesses", [])
          if w.get("focus")]
    tf = narrative.get("recommended_focus") or []
    weak = list(dict.fromkeys(nw)) if nw else None
    master = list(dict.fromkeys(weak + list(tf))) if (nw and tf) else None
    return weak, master


def _resources_for(db, step) -> list[dict]:
    """Resolve step resources to lightweight dicts; [] when none."""
    return [{
        "id": r.id, "title": r.title, "url": r.url, "type": r.type}
        for r in catalog_repository.get_resources_by_ids(
            db, step.resource_ids or [])]


def _assemble_grade_result(passed, score, correct, total, weak_points,
                           topics_to_master, resources, completed, next_level,
                           current_level, assessment_id, graded) -> dict:
    """Pack the grade result dict from computed pieces."""
    return {
        "passed": passed,
        "score": round(score, 4),
        "correct": correct,
        "total": total,
        "weak_points": weak_points,
        "topics_to_master": topics_to_master,
        "resources": resources,
        "completed": completed,
        "proficiency_level": next_level,
        "next_level": next_level,
        "level_passed": next_level >= current_level,
        "assessment_id": assessment_id,
        "graded": graded,
    }


def _grade(db: Session, user_id: int, ctx, data, locale: str):
    """Grade answers, persist level + weak points, complete step on pass."""
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
    next_level = _persist_grade(
        db, user_id, skill, weak_points, correct, total, difficulty,
        current_level)
    if not passed and _ai_active():
        d_weak, d_master = _diagnostic_for_fail(
            db, skill, topics, correct, total, next_level, locale)
        weak_points = d_weak if d_weak is not None else weak_points
        topics_to_master = d_master if d_master is not None else topics_to_master
    completed = bool(passed)
    if passed:
        learning_service.complete_step(db, user_id, ctx["step"].id)
    resources = _resources_for(db, step)
    return _assemble_grade_result(
        passed, score, correct, total, weak_points, topics_to_master,
        resources, completed, next_level, current_level, assessment_id,
        graded), None, None


def grade_step_test(db: Session, user_id: int, step_id: int, data: dict,
                    locale: str = "en"):
    """Entry point: resolve context then grade; (result, error, status)."""
    ctx, err, status = _step_context(db, user_id, step_id)
    if err:
        return None, err, status
    return _grade(db, user_id, ctx, data, locale)
