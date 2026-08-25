"""Assessments router — questions and scored submissions.

Wires /api/assessments to services/assess_service.py (Task 2). The submit
body model lives here (M3 deferred finding: services leave input_data
untyped). Questions are keyed by skill_id per the reduced schema.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.events.publisher import send_event
from backend.policies.auth_policy import get_current_user
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.services import assess_service


class AssessmentSubmitInput(BaseModel):
    """POST /api/assessments/submit body (router-side, M3 resolution).

    answers is the ordered list of selected option indices, graded by
    assess_service.submit_result against assessment_questions.correct_index.
    """
    assessment_id: int
    answers: List[int] = []


router = APIRouter()


def _questions_for_skill_id(db: Session, skill_id: int) -> List[dict]:
    """Build the frozen question payload for one skill via its assessment.

    Shape mirrors assess_service.questions_for_skill (string ids
    "<skill>_q<i>", skill name, text, options) but resolves directly by
    skill_id as the reduced-schema route requires.
    """
    skill = catalog_repository.get_skill(db, skill_id)
    if not skill:
        return []
    assessment = arepo.get_assessments_for_skills(db, [skill_id]).get(skill_id)
    if not assessment:
        return []
    questions = []
    for i, q in enumerate(arepo.get_questions(db, assessment.id)):
        questions.append({
            "id": f"{assess_service.normalize_key(skill.name).lower()}_q{i}",
            "skill": skill.name,
            "text": q.prompt,
            "options": q.options or [],
        })
    return questions


@router.get("/assessments/{skill_id}/questions")
def get_assessment_questions(skill_id: int, db: Session = Depends(get_db),
                             current_user=Depends(get_current_user)):
    """Return the question payload for a skill. Calls the assess repository;
    consumed by the wizard assessment step (skill_id-keyed)."""
    return _questions_for_skill_id(db, skill_id)


@router.get("/assessments/role/{job_role_title}")
def get_role_questions(job_role_title: str, db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    """Return question payloads for every quiz-covered skill of a job role.

    Delegates to assess_service.questions_for_skill, whose ids
    ("<normalized_skill>_q<i>") match the wizard answer keys consumed by
    learning_service._score_answers; called by PathWizard's assessment
    step after goal selection."""
    return assess_service.questions_for_skill(db, job_role_title)


@router.post("/assessments/submit")
def submit_assessment(data: AssessmentSubmitInput, db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    """Grade a submission and persist the result + proficiency. Calls
    assess_service.submit_result; broadcasts an assessment_completed SSE event."""
    result, error, status = assess_service.submit_result(db, current_user, data)
    if error:
        raise HTTPException(status_code=status, detail=error)
    send_event(current_user.id, "assessment_completed", {
        "assessment_id": data.assessment_id,
        "score": result["score"],
        "total_questions": result["total_questions"],
    })
    return result
