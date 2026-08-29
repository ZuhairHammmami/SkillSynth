"""Evaluations service — admin CRUD for assessments and their questions.

Called by routers/evaluations_admin.py. Returns (result, error) tuples so
the thin router can map errors through routers/error_mapping.status_for_error
('*not found*' → 404, restricted-delete conflicts → 409, invalid refs →
400). Option/position/index rules and the last-question guard live here;
persistence in assess_repository; skill-FK checks via catalog_repository.
"""

from backend.repositories import assess_repository as repo
from backend.repositories import catalog_repository
from backend.services import catalog_integrity


def _serialize_question(q) -> dict:
    """Question row → wire dict for detail payloads."""
    return {
        "id": q.id, "assessment_id": q.assessment_id, "position": q.position,
        "prompt": q.prompt, "options": q.options, "correct_index": q.correct_index,
    }


def _serialize_assessment(db, a, with_questions: bool = False) -> dict:
    """Assessment row → wire dict; additively includes skill name + counts.

    `with_questions` appends the ordered question list (detail endpoint);
    the flat list keeps skill_name + question_count only."""
    skill = catalog_repository.get_skill(db, a.skill_id) if a.skill_id else None
    out = {
        "id": a.id, "skill_id": a.skill_id,
        "skill_name": skill.name if skill else None,
        "title": a.title, "description": a.description,
        "assessment_type": a.description, "passing_score": a.pass_score or 60,
        "question_count": repo.count_questions(db, a.id),
    }
    if with_questions:
        out["questions"] = [_serialize_question(q)
                            for q in repo.get_questions(db, a.id)]
    return out


def list_assessments(db) -> list[dict]:
    """All assessments serialized; admin assessments page listing."""
    return [_serialize_assessment(db, a)
            for a in repo.get_all_assessments(db)]


def get_assessment_detail(db, assessment_id: int) -> tuple[dict | None, str | None]:
    """Fetch assessment metadata + ordered questions; (payload, error).

    Called by GET /admin/assessments/{id}; missing rows surface 404."""
    assessment = repo.get_assessment(db, assessment_id)
    if not assessment:
        return None, "Assessment not found"
    return _serialize_assessment(db, assessment, with_questions=True), None


def create_assessment(db, data) -> tuple[dict | None, str | None]:
    """Skill-FK guarded assessment insert; (payload, error) tuple.

    Called by POST /admin/assessments; unknown skill_id surfaces 400
    via the catalog FK guard."""
    error = catalog_integrity.ensure_resource_skill_exists(db, data.skill_id)
    if error:
        return None, error
    assessment = repo.create_assessment(db, data.skill_id, data.title,
                                        data.description, data.pass_score)
    return _serialize_assessment(db, assessment), None


def update_assessment(db, assessment_id: int, data) -> tuple[dict | None, str | None]:
    """Partial assessment update with skill-FK guard; (payload, error).

    Called by PUT /admin/assessments/{id}; missing row 404, unknown
    skill_id 400."""
    assessment = repo.get_assessment(db, assessment_id)
    if not assessment:
        return None, "Assessment not found"
    fields = data.model_dump(exclude_unset=True)
    if "skill_id" in fields:
        error = catalog_integrity.ensure_resource_skill_exists(
            db, fields["skill_id"])
        if error:
            return None, error
    updated = repo.update_assessment(db, assessment, fields)
    return _serialize_assessment(db, updated), None


def delete_assessment(db, assessment_id: int,
                      force: bool = False) -> tuple[bool, str | dict | None]:
    """Restricted-delete with dependent census; (ok, error) tuple.

    Called by DELETE /admin/assessments/{id}; missing row 404, existing
    dependents 409 unless ?force=true bypasses the guard (cascade via
    model FK rules)."""
    if not repo.get_assessment(db, assessment_id):
        return False, "Assessment not found"
    if not force:
        conflict = catalog_integrity.assessment_delete_conflict(
            db, assessment_id)
        if conflict:
            return False, conflict
    if not repo.delete_assessment(db, assessment_id):
        return False, "Assessment not found"
    return True, None


def _ordered_questions(db, assessment_id: int) -> list:
    """Questions of an assessment ordered by current position."""
    return repo.get_questions(db, assessment_id)


def _reposition_add(db, assessment_id: int, position: int | None) -> int:
    """Compute the position for a new question and shift later rows down.

    With no explicit position the question joins at the end (max+1)."""
    rows = _ordered_questions(db, assessment_id)
    next_pos = (rows[-1].position + 1) if rows else 1
    if position is None or position >= next_pos:
        return next_pos
    for q in rows:
        if q.position >= position:
            q.position += 1
    db.commit()
    return position


def add_question(db, assessment_id: int, data) -> tuple[dict | None, str | None]:
    """Insert one question with option/index + position rules; (payload, err)."""
    if not repo.get_assessment(db, assessment_id):
        return None, "Assessment not found"
    if len(data.options) < 2:
        return None, "Options must contain at least 2 entries"
    if not (0 <= data.correct_index < len(data.options)):
        return None, "correct_index must be within the options range"
    position = _reposition_add(db, assessment_id, data.position)
    question = repo.add_question(db, assessment_id, position, data.prompt,
                                 data.options, data.correct_index)
    return _serialize_question(question), None


def _reposition_move(db, assessment_id: int, question,
                     new_position: int) -> None:
    """Shift neighbours up/down when a row's position changes."""
    rows = _ordered_questions(db, assessment_id)
    old = question.position
    if new_position == old:
        return
    for q in rows:
        if q.id == question.id:
            continue
        if new_position > old and old < q.position <= new_position:
            q.position -= 1
        elif new_position < old and new_position <= q.position < old:
            q.position += 1
    db.commit()


def update_question(db, assessment_id: int, question_id: int,
                    data) -> tuple[dict | None, str | None]:
    """Partial question update with option/index + re-positioning rules.

    Called by PUT .../questions/{qid}; missing rows surface 404, invalid
    options/correct_index 400."""
    if not repo.get_assessment(db, assessment_id):
        return None, "Assessment not found"
    question = repo.get_question(db, question_id)
    if not question or question.assessment_id != assessment_id:
        return None, "Question not found"
    fields = data.model_dump(exclude_unset=True)
    options = fields.get("options", question.options)
    if len(options) < 2:
        return None, "Options must contain at least 2 entries"
    new_index = fields.get("correct_index", question.correct_index)
    if not (0 <= new_index < len(options)):
        return None, "correct_index must be within the options range"
    new_position = fields.get("position")
    if new_position is not None and new_position != question.position:
        _reposition_move(db, assessment_id, question, new_position)
    updated = repo.update_question(db, question, fields)
    return _serialize_question(updated), None


def delete_question(db, assessment_id: int,
                    question_id: int) -> tuple[bool, str | None]:
    """Delete one question then renumber survivors; last row is a 400.

    Called by DELETE .../questions/{qid}; requires ≥1 question to remain
    so every quiz keeps a question."""
    if not repo.get_assessment(db, assessment_id):
        return False, "Assessment not found"
    question = repo.get_question(db, question_id)
    if not question or question.assessment_id != assessment_id:
        return False, "Question not found"
    if repo.count_questions(db, assessment_id) <= 1:
        return False, "Assessment must keep at least one question"
    repo.delete_question(db, question)
    survivors = _ordered_questions(db, assessment_id)
    repo.renumber_questions(db, survivors)
    return True, None
