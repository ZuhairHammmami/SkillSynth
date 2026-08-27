"""Placement self-assessment persistence + path shaping tests."""

from backend.dto.catalog import SkillCreate
from backend.dto.learning import GeneratePathIn
from backend.entities.identity import User
from backend.entities.learning import UserSkill
from backend.repositories import catalog_repository
from backend.services import learning_service


def _make_user(db, email):
    """Insert an isolated user with no prior user_skills."""
    user = User(email=email, hashed_password="x", is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _build_role(db, skills):
    """Create a job role linked to the given skill rows."""
    role = catalog_repository.create_job_role(
        db, "SelfAssessRole", "role for placement", "test")
    catalog_repository.set_job_role_skills(db, role.id, [s.id for s in skills])
    return role


def test_self_assessment_excludes_mastered_and_persists(db_session):
    """Self-report {A:5,B:2,C:0} excludes A, keeps B/C, persists A=5."""
    cat = catalog_repository.get_all_categories(db_session)[0]
    base = dict(difficulty_level=5, estimated_hours=10, category_id=cat.id)
    a = catalog_repository.create_skill(db_session, SkillCreate(name="A", **base))
    b = catalog_repository.create_skill(db_session, SkillCreate(name="B", **base))
    c = catalog_repository.create_skill(db_session, SkillCreate(name="C", **base))
    _build_role(db_session, [a, b, c])
    user = _make_user(db_session, "selfassess@test.io")

    result, error = learning_service.generate_path(
        db_session, user,
        GeneratePathIn(goal="SelfAssessRole", weekly_hours=10,
                       preferences={}, answers={"A": 5, "B": 2, "C": 0}))

    assert error is None
    step_ids = {s["skill_id"] for s in result["steps"]}
    assert a.id not in step_ids
    assert b.id in step_ids and c.id in step_ids
    us = db_session.query(UserSkill).filter_by(
        user_id=user.id, skill_id=a.id).first()
    assert us is not None and us.proficiency_level == 5
