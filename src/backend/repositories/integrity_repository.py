"""Integrity repository — dependent-row counters for restricted deletes.

Called exclusively by services/catalog_integrity.py before catalog
deletes; pure data access: no business rules, no serialization. Count
keys mirror migrations/003_reduced_schema.sql relations.
"""

from sqlalchemy.orm import Session

from backend.entities.assessment import (
    Assessment, AssessmentQuestion, AssessmentResult,
)
from backend.entities.catalog import (
    JobRoleSkill, Resource, Skill, SkillPrerequisite,
)
from backend.entities.engagement import ActivityLog
from backend.entities.identity import User
from backend.entities.learning import (
    Path, PathStep, StepProgress, UserSkill,
)


def count_skill_dependents(db: Session, skill_id: int) -> dict[str, int]:
    """Non-zero dependent counts blocking DELETE /admin/skills.

    Called by catalog_integrity.skill_delete_conflict; mapping/learner
    rows cascade on force-delete, path_steps.skill_id is set null
    (steps survive detached), resources and assessments set null, and
    both skill_prerequisites directions are reported
    separately (`requires` = this skill's own edges, `required_by` =
    edges where other skills list it as prerequisite).
    """
    counts = {
        "job_role_skills": db.query(JobRoleSkill)
            .filter(JobRoleSkill.skill_id == skill_id).count(),
        "user_skills": db.query(UserSkill)
            .filter(UserSkill.skill_id == skill_id).count(),
        "path_steps": db.query(PathStep)
            .filter(PathStep.skill_id == skill_id).count(),
        "resources": db.query(Resource)
            .filter(Resource.skill_id == skill_id).count(),
        "assessments": db.query(Assessment)
            .filter(Assessment.skill_id == skill_id).count(),
        "requires": db.query(SkillPrerequisite)
            .filter(SkillPrerequisite.skill_id == skill_id).count(),
        "required_by": db.query(SkillPrerequisite)
            .filter(SkillPrerequisite.prerequisite_id == skill_id).count(),
    }
    return {name: cnt for name, cnt in counts.items() if cnt}


def count_category_skills(db: Session, category_id: int) -> dict[str, int]:
    """Non-zero skill census blocking DELETE /admin/categories/{id}.

    Called by catalog_integrity.category_delete_conflict; force lets the
    skills.category_id ON DELETE SET NULL rule detach them instead.
    """
    cnt = db.query(Skill).filter(Skill.category_id == category_id).count()
    return {"skills": cnt} if cnt else {}


def count_job_role_dependencies(db: Session, job_role_id: int) -> dict[str, int]:
    """Non-zero mapping census blocking DELETE /admin/job-roles/{id}.

    Called by catalog_integrity.job_role_delete_conflict; force cascades
    the job_role_skills rows away with the role.
    """
    cnt = db.query(JobRoleSkill)\
        .filter(JobRoleSkill.job_role_id == job_role_id).count()
    return {"job_role_skills": cnt} if cnt else {}


def count_user_dependents(db: Session, user_id: int) -> dict[str, int]:
    """Non-zero dependent census blocking DELETE /admin/users/{id}.

    Called by catalog_integrity.user_delete_conflict; covers every row
    with an FK to users.id (paths, assessment_results, user_skills,
    step_progress and the nullable activity_log audit trail).
    """
    counts = {
        "paths": db.query(Path).filter(Path.user_id == user_id).count(),
        "assessment_results": db.query(AssessmentResult)
            .filter(AssessmentResult.user_id == user_id).count(),
        "user_skills": db.query(UserSkill)
            .filter(UserSkill.user_id == user_id).count(),
        "step_progress": db.query(StepProgress)
            .filter(StepProgress.user_id == user_id).count(),
        "activity_log": db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id).count(),
    }
    return {name: cnt for name, cnt in counts.items() if cnt}


def count_resource_dependents(db: Session, resource_id: int) -> dict[str, int]:
    """Non-zero dependent census blocking DELETE /api/admin/resources/{id}.

    Called by catalog_integrity.resource_delete_conflict; path_steps keeps
    resource_ids as a JSON array (documented 3NF exception) so the
    reference is found by scanning the non-null lists in Python.
    """
    steps = db.query(PathStep).filter(
        PathStep.resource_ids.isnot(None)).all()
    refs = sum(1 for s in steps if resource_id in (s.resource_ids or []))
    return {"path_steps": refs} if refs else {}


def count_assessment_dependents(db: Session, assessment_id: int) -> dict[str, int]:
    """Non-zero dependent census blocking DELETE /api/admin/assessments/{id}.

    Called by catalog_integrity.assessment_delete_conflict; counts scored
    results and questions plus path_steps that embed the id in their
    assessment_ids JSON array (documented 3NF exception).
    """
    results = db.query(AssessmentResult).filter(
        AssessmentResult.assessment_id == assessment_id).count()
    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.assessment_id == assessment_id).count()
    steps = db.query(PathStep).filter(
        PathStep.assessment_ids.isnot(None)).all()
    refs = sum(1 for s in steps if assessment_id in (s.assessment_ids or []))
    counts: dict[str, int] = {}
    if results:
        counts["assessment_results"] = results
    if questions:
        counts["assessment_questions"] = questions
    if refs:
        counts["path_steps"] = refs
    return counts
