"""Pure/stateless helpers for step tests (deterministic math + payloads).

Kept separate from step_test_service.py to honor the 300-line file limit;
these functions perform no DB writes and have no side effects (objects they
touch are passed in). step_test_service re-exports the names its callers
and tests rely on (compute_effective_difficulty, _topics_for, _score_answers,
_assemble_grade_result), so the seam surface is unchanged.
"""

from __future__ import annotations

_PASS_THRESHOLD = 0.6
MASTERY_SCALE = 5


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


def _select_topics(skill, step, eff_level) -> list[str]:
    """Leveled placeholder topics when eff_level>1, else skill/step topics.

    Deterministic request-path topic selection: never calls the LLM. Leveled
    placeholders mirror llm_pipeline._seeded_topics so AI enrichment later
    refines them via ai_step_quiz_ready / ai_step_diagnostic.
    """
    if eff_level > 1:
        return [f"Topic {i} for {skill.name} (level {eff_level})"
                for i in range(1, min(3, eff_level) + 1)]
    return _topics_for(skill, step)


def _decorate_questions(questions: list[dict], topics) -> list[dict]:
    """Tag each question with its topic and drop internal assessment_id."""
    out = []
    for i, q in enumerate(questions):
        row = dict(q)
        row["topic"] = topics[i % len(topics)] if topics else None
        row.pop("assessment_id", None)
        out.append(row)
    return out


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
