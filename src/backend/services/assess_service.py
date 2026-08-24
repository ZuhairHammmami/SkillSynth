"""Assessment service — question payloads and scored submissions.

Called by the assessments routers (Task 3). Questions come from the
normalized assessment_questions table; submissions grade against
correct_index, persist an AssessmentResult and upsert user_skills.
"""

from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository

MASTERY_SCALE = 5


def _normalize_key(name: str) -> str:
    """Historical skill-name → assessment key normalization."""
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
                "id": f"{_normalize_key(skill.name).lower()}_q{i}",
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
    clamped to 0..5 with last_assessed_at stamped. Returns
    (payload|None, error|None, http_status).
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
    return _serialize_result(result, total, responses), None, 200


def get_assessment_by_id(db, assessment_id: int):
    """Pass-through lookup used by routers after submission."""
    return arepo.get_assessment(db, assessment_id)
