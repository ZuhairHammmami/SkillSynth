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


def compute_effective_difficulty(skill, user_skill, topics: list[str]) -> int:
    """Effective quiz difficulty for a step test.

    Base difficulty rises by up to +2 for topics the learner has already
    cleared (topics NOT in weak_points), so the local AI writes harder
    questions as advanced topics are mastered. Clamped to 1..5. Seeded
    fallback bank ignores difficulty; the bonus is realized on the AI path.
    """
    base = int(skill.difficulty_level or 1)
    weak = set(user_skill.weak_points or []) if user_skill else set()
    mastered = [t for t in topics if t and t not in weak]
    bonus = min(2, len(mastered))
    return min(5, base + bonus)


def _proficiency(db: Session, user_id: int, skill_id: int) -> int:
    """Current proficiency_level for the skill, default 0."""
    us = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill_id).first()
    return us.proficiency_level if us else 0


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
    return bool(settings.AI_ENABLED) and llm_pipeline._engine_available()


def _leveled_topics(skill_name: str, level: int) -> list[str]:
    """Topics for a leveled step test; AI when active, else seeded fallback.

    Callee of generate_step_test; calls llm_pipeline.generate_skill_topics
    and, on an unavailable engine or LLM failure, delegates to the seeded
    deterministic fallback so tests stay reproducible without the LLM.
    """
    if _ai_active():
        try:
            return llm_pipeline.generate_skill_topics(skill_name, level)
        except llm_pipeline.LLMOperationError:
            pass
    count = min(3, level + 1)
    return [f"Topic {i} for {skill_name} (level {level})"
            for i in range(1, count + 1)]


def generate_step_test(db: Session, user_id: int, step_id: int,
                        locale: str = "en", level: int = None,
                        ai_enabled: bool = None):
    """Build the synchronous step test payload; (payload, error, status).

    Accepts an optional level (defaults to the step's current_level, else 1)
    and an optional ai_enabled override; for level > 1 topics come from the
    leveled topic generator, otherwise from the skill/step objectives.
    """
    ctx, err, status = _step_context(db, user_id, step_id)
    if err:
        return None, err, status
    skill, step = ctx["skill"], ctx["step"]
    eff_level = level if level is not None else (step.current_level or 1)
    ai = ai_enabled if ai_enabled is not None else _ai_active()
    if eff_level > 1:
        topics = _leveled_topics(skill.name, eff_level)
    else:
        topics = _topics_for(skill, step)
    proficiency = _proficiency(db, user_id, skill.id)
    user_skill = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    difficulty = compute_effective_difficulty(skill, user_skill, topics)
    questions: list[dict] = []
    assessment_id: Optional[int] = None
    if ai:
        try:
            raw = llm_pipeline.generate_skill_quiz(
                skill.name, difficulty=difficulty,
                n=max(_AI_N, len(topics)),
                proficiency_level=proficiency, topics=topics or None,
                locale=locale)
            assessment = arepo.create_assessment_with_questions(
                db, skill.id, f"[AI] {skill.name} — step {step_id} test",
                "Targeted step completion test", 60, raw)
            assessment_id = assessment.id
            qs = arepo.get_questions(db, assessment.id)
            questions = [{
                "id": q.id, "text": q.prompt, "options": list(q.options),
                "correct_index": q.correct_index,
            } for q in qs]
        except llm_pipeline.LLMOperationError:
            questions = []
    if not questions:
        seeded = _seeded_questions(db, skill)
        if not seeded:
            return None, "No questions available for this skill", 400
        questions = seeded
        assessment_id = seeded[0]["assessment_id"]
    for i, q in enumerate(questions):
        q["topic"] = topics[i % len(topics)] if topics else None
        q.pop("assessment_id", None)
    payload = {
        "step_id": step_id,
        "skill": {"id": skill.id, "name": skill.name,
                  "difficulty_level": skill.difficulty_level,
                  "effective_difficulty": difficulty},
        "topics": topics,
        "assessment_id": assessment_id,
        "questions": questions,
    }
    return payload, None, None


def _grade(db: Session, user_id: int, ctx, data, locale: str):
    """Grade submitted answers and persist weak points + proficiency."""
    skill, step = ctx["skill"], ctx["step"]
    topics = _topics_for(skill, step)
    answers = data.get("answers") or {}
    assessment_id = data.get("assessment_id")
    if not answers:
        return None, "No answers submitted", 400
    qs = arepo.get_questions(db, assessment_id) if assessment_id else []
    topic_by_id = {q.id: (topics[i % len(topics)] if topics else None)
                   for i, q in enumerate(qs)}
    rows = {q.id: q for q in qs}
    total = 0
    correct_count = 0
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
        if is_correct:
            correct_count += 1
        else:
            tp = topic_by_id.get(qid)
            if tp and tp not in weak:
                weak.append(tp)
        graded.append({"question_id": qid, "correct": is_correct,
                       "selected": sel, "correct_index": q.correct_index})
    if total == 0:
        return None, "No valid answers", 400
    score = correct_count / total
    passed = score >= _PASS_THRESHOLD
    weak_points = list(dict.fromkeys(weak))
    if topics:
        remaining = [t for t in topics if t not in weak_points]
        topics_to_master = weak_points + remaining
    else:
        topics_to_master = weak_points

    us = db.query(UserSkill).filter_by(
        user_id=user_id, skill_id=skill.id).first()
    if not us:
        us = UserSkill(user_id=user_id, skill_id=skill.id,
                       proficiency_level=0)
        db.add(us)
    current_level = us.proficiency_level or 0
    difficulty = compute_effective_difficulty(skill, us, topics)
    attempt_no = len(arepo.results_for_user(db, user_id))
    verdict = assess_service.review_level(
        correct_count, total, difficulty, attempt_no, current_level)
    next_level = verdict["final_level"]
    us.proficiency_level = next_level
    merged = list(us.weak_points or [])
    for t in weak_points:
        if t not in merged:
            merged.append(t)
    us.weak_points = merged
    db.commit()

    if (not passed and _ai_active()):
        per_skill = [{
            "skill": skill.name, "correct": correct_count, "total": total,
            "assessed_level": new_level,
            "gap": max(0, learning_service.MASTERY_LEVEL - new_level)}]
        narrative = llm_pipeline.analyze_diagnostic(
            per_skill, topics=topics, locale=locale)
        if narrative:
            nw = [w.get("focus") for w in narrative.get("weaknesses", [])
                  if w.get("focus")]
            if nw:
                weak_points = list(dict.fromkeys(nw))
            tf = narrative.get("recommended_focus") or []
            if tf:
                topics_to_master = list(dict.fromkeys(weak_points + list(tf)))

    completed = False
    if passed:
        learning_service.complete_step(db, user_id, ctx["step"].id)
        completed = True

    resources = [{
        "id": r.id, "title": r.title, "url": r.url, "type": r.type}
        for r in catalog_repository.get_resources_by_ids(
            db, step.resource_ids or [])]

    return {
        "passed": passed,
        "score": round(score, 4),
        "correct": correct_count,
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
    }, None, None


def grade_step_test(db: Session, user_id: int, step_id: int, data: dict,
                    locale: str = "en"):
    """Entry point: resolve context then grade; (result, error, status)."""
    ctx, err, status = _step_context(db, user_id, step_id)
    if err:
        return None, err, status
    return _grade(db, user_id, ctx, data, locale)
