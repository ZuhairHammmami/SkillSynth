"""Assessment repository — assessments, questions, results, user_skills.

Called by services/assess_service.py, services/analytics_service.py and
services/learning_service.py (user_skills upserts during generation).
"""

from datetime import datetime, UTC

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.entities.assessment import (
    Assessment, AssessmentQuestion, AssessmentResult,
)
from backend.entities.catalog import Skill
from backend.entities.learning import UserSkill


# ── Assessments + questions ──────────────────────────────────────────

def get_assessment(db: Session, assessment_id: int) -> Assessment | None:
    """Fetch one assessment by PK; scoring entry point."""
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()


def get_assessments_for_skills(db: Session,
                               skill_ids: list[int]) -> dict[int, Assessment]:
    """skill_id -> first assessment map for the given skills."""
    if not skill_ids:
        return {}
    rows = (
        db.query(Assessment)
        .filter(Assessment.skill_id.in_(skill_ids))
        .order_by(Assessment.id)
        .all()
    )
    out: dict[int, Assessment] = {}
    for row in rows:
        out.setdefault(row.skill_id, row)
    return out


def get_all_assessments(db: Session) -> list[Assessment]:
    """Full listing; admin catalog page."""
    return db.query(Assessment).order_by(Assessment.id).all()


def count_assessments(db: Session) -> int:
    """Total assessments; system health report."""
    return db.query(Assessment).count()


def get_questions(db: Session, assessment_id: int) -> list[AssessmentQuestion]:
    """A quiz's questions ordered by position; payload + grading."""
    return (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.assessment_id == assessment_id)
        .order_by(AssessmentQuestion.position)
        .all()
    )


def delete_assessment(db: Session, assessment_id: int) -> bool:
    """Hard-delete a quiz (questions/results cascade); False if absent."""
    assessment = get_assessment(db, assessment_id)
    if not assessment:
        return False
    db.delete(assessment)
    db.commit()
    return True


# ── Results ───────────────────────────────────────────────────────────

def create_result(db: Session, user_id: int, assessment_id: int,
                  score: int, passed: bool) -> AssessmentResult:
    """Persist one scored attempt with completed_at now; commits."""
    result = AssessmentResult(
        user_id=user_id, assessment_id=assessment_id,
        score=score, passed=passed, completed_at=datetime.now(UTC),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def count_results(db: Session) -> int:
    """Total attempts; admin aggregated report."""
    return db.query(AssessmentResult).count()


def average_score(db: Session) -> float:
    """Mean attempt score across all users; admin aggregated report."""
    return db.query(func.avg(AssessmentResult.score)).scalar() or 0.0


def results_for_user(db: Session, user_id: int) -> list[AssessmentResult]:
    """A user's attempts, newest first; weakness analysis input."""
    return (
        db.query(AssessmentResult)
        .filter(AssessmentResult.user_id == user_id)
        .order_by(AssessmentResult.completed_at.desc())
        .all()
    )


# ── user_skills ───────────────────────────────────────────────────────

def get_skill_profile(db: Session, user_id: int) -> dict[str, int]:
    """{skills.name: proficiency_level} via join — the ProfileOut
    skill_profile synthesis and analytics source of truth."""
    rows = (
        db.query(Skill.name, UserSkill.proficiency_level)
        .join(Skill, Skill.id == UserSkill.skill_id)
        .filter(UserSkill.user_id == user_id)
        .all()
    )
    return {name: level for name, level in rows}


def upsert_user_skill(db: Session, user_id: int, skill_id: int,
                      proficiency_level: int) -> None:
    """Insert or overwrite one proficiency row; stamps last_assessed_at."""
    row = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.skill_id == skill_id).first()
    if row is None:
        row = UserSkill(user_id=user_id, skill_id=skill_id)
        db.add(row)
    row.proficiency_level = proficiency_level
    row.last_assessed_at = datetime.now(UTC)


def create_assessment_with_questions(db: Session, skill_id: int | None,
                                     title: str, description: str,
                                     pass_score: int,
                                     questions: list[dict]) -> Assessment:
    """Persist one assessment plus positional questions; commits.

    Sole producer of AI-generated quizzes (routers/ai.py Task 6);
    reuses AssessmentQuestion so grading/_grade works unchanged.
    """
    assessment = Assessment(skill_id=skill_id, title=title,
                            description=description,
                            pass_score=pass_score)
    db.add(assessment)
    db.flush()
    for pos, q in enumerate(questions, start=1):
        db.add(AssessmentQuestion(
            assessment_id=assessment.id, position=pos, prompt=q["text"],
            options=q["options"], correct_index=q["correct_index"]))
    db.commit()
    db.refresh(assessment)
    return assessment
