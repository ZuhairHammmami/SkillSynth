"""Evaluations-admin router — assessments and their questions CRUD.

Mounted under /api/admin by backend/main.py beside routers/admin.py and
routers/catalog_admin.py. Every route is admin-only via the router-level
require_admin dependency. Thin handlers delegate to
services/evaluations_service.py; `(result, error)` tuples map through
routers/error_mapping.status_for_error: '*not found*' → 404, restricted-
delete conflicts → 409, invalid references/validation → 400.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.admin import (
    AssessmentCreate, AssessmentUpdate, QuestionCreate, QuestionUpdate,
)
from backend.policies.auth_policy import require_admin
from backend.routers.error_mapping import status_for_error
from backend.services import evaluations_service

router = APIRouter(dependencies=[Depends(require_admin)])


def _fail(error) -> None:
    """Raise the mapped HTTPException for a service error payload."""
    raise HTTPException(status_code=status_for_error(error), detail=error)


def _respond(result, error):
    """Return the payload, or raise the mapped 404/409/400 on error."""
    if error:
        _fail(error)
    return result


# ── Assessments ───────────────────────────────────────────────────────

@router.get("/assessments")
def list_assessments(db: Session = Depends(get_db)):
    """List all assessments with skill name + question count; admin page."""
    return evaluations_service.list_assessments(db)


@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Assessment metadata + ordered questions; 404 when missing."""
    result, error = evaluations_service.get_assessment_detail(
        db, assessment_id)
    return _respond(result, error)


@router.post("/assessments")
def create_assessment(data: AssessmentCreate, db: Session = Depends(get_db)):
    """Create an assessment; unknown skill_id maps to 400."""
    result, error = evaluations_service.create_assessment(db, data)
    return _respond(result, error)


@router.put("/assessments/{assessment_id}")
def update_assessment(assessment_id: int, data: AssessmentUpdate,
                      db: Session = Depends(get_db)):
    """Update assessment metadata; 404 missing / 400 unknown skill."""
    result, error = evaluations_service.update_assessment(
        db, assessment_id, data)
    return _respond(result, error)


@router.delete("/assessments/{assessment_id}")
def delete_assessment(assessment_id: int, force: bool = False,
                      db: Session = Depends(get_db)):
    """Restricted-delete an assessment (dependent census guarded); 409
    with dependents unless ?force=true lets DB cascade rules apply."""
    ok, error = evaluations_service.delete_assessment(
        db, assessment_id, force)
    if not ok:
        _fail(error)
    return {"detail": "Deleted successfully"}


# ── Questions ─────────────────────────────────────────────────────────

@router.post("/assessments/{assessment_id}/questions")
def add_question(assessment_id: int, data: QuestionCreate,
                 db: Session = Depends(get_db)):
    """Add a question (auto-positions unless a position is supplied)."""
    result, error = evaluations_service.add_question(
        db, assessment_id, data)
    return _respond(result, error)


@router.put("/assessments/{assessment_id}/questions/{question_id}")
def update_question(assessment_id: int, question_id: int,
                    data: QuestionUpdate, db: Session = Depends(get_db)):
    """Update prompt/options/correct_index/position; re-slots neighbours."""
    result, error = evaluations_service.update_question(
        db, assessment_id, question_id, data)
    return _respond(result, error)


@router.delete("/assessments/{assessment_id}/questions/{question_id}")
def delete_question(assessment_id: int, question_id: int,
                    db: Session = Depends(get_db)):
    """Delete one question and renumber the rest; 400 if it is the last."""
    ok, error = evaluations_service.delete_question(
        db, assessment_id, question_id)
    if not ok:
        _fail(error)
    return {"detail": "Deleted successfully"}
