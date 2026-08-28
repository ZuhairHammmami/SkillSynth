"""tests/test_proficiency.py — PUT /api/learning/skills/{id}/proficiency."""
import uuid

import pytest

from backend.entities.engagement import ActivityLog
from backend.entities.identity import User
from backend.entities.learning import Path, PathStep, UserSkill

_TOUCHED = set()
_TOUCHED_USERS = set()


def _veteran_id(db_session):
    """id of the seeded veteran account (authed by auth_headers)."""
    return db_session.query(User).filter_by(
        email="veteran@skillsynth.io").first().id


@pytest.fixture(autouse=True)
def purge_proficiency_rows(db_session):
    """Delete this module's authored rows so pinned seed counts stay green.

    Removes the rate.proficiency.set activity rows, the UserSkill rows
    the route wrote for the authed account, and any second user/step
    created to prove per-user scoping (cascade drops its path + step).
    """
    yield
    db_session.query(ActivityLog).filter(
        ActivityLog.action == "rate.proficiency.set").delete(
        synchronize_session=False)
    if _TOUCHED:
        db_session.query(UserSkill).filter(
            UserSkill.user_id == _veteran_id(db_session),
            UserSkill.skill_id.in_(list(_TOUCHED))).delete(
            synchronize_session=False)
    if _TOUCHED_USERS:
        db_session.query(User).filter(
            User.id.in_(list(_TOUCHED_USERS))).delete(
            synchronize_session=False)
    _TOUCHED.clear()
    _TOUCHED_USERS.clear()
    db_session.commit()


def _veteran_steps(db_session, skill_id):
    """The authed (veteran) user's PathSteps for a skill, if any.

    The route scopes ladder updates to the current user, so these are
    the only steps that should move.
    """
    query = (db_session.query(PathStep)
             .join(Path, PathStep.path_id == Path.id)
             .filter(Path.user_id == _veteran_id(db_session)))
    if skill_id is None:
        query = query.filter(PathStep.skill_id.isnot(None))
    else:
        query = query.filter(PathStep.skill_id == skill_id)
    return query.all()


def _rate_veteran_step(db_session):
    """(skill_id, step_id) of a seeded veteran step, else (None, None)."""
    steps = _veteran_steps(db_session, None)
    if not steps:
        return None, None
    skill_id = steps[0].skill_id
    _TOUCHED.add(skill_id)
    return skill_id, steps[0].id


def _second_user_step(db_session, api_client, skill_id):
    """A non-authed user's PathStep for skill_id (existing or created).

    Returns the step plus None when an existing seed row was reused, or
    a fresh user id when a second user/path/step had to be created (the
    purge fixture deletes the created user via cascade).
    """
    from backend.repositories import learning_repository as lrepo

    other = (db_session.query(PathStep)
             .join(Path, PathStep.path_id == Path.id)
             .filter(Path.user_id != _veteran_id(db_session),
                     PathStep.skill_id == skill_id)
             .first())
    if other:
        return other, None
    email = f"other_{uuid.uuid4().hex[:8]}@test.com"
    api_client.post("/api/auth/register", json={
        "email": email, "password": "Other@123456"})
    user = db_session.query(User).filter_by(email=email).first()
    path = lrepo.create_path(db_session, user.id, "scoping path")
    step = lrepo.create_step(db_session, path.id, 1, "shared skill step")
    step.skill_id = skill_id
    db_session.commit()
    _TOUCHED_USERS.add(user.id)
    return step, user.id


def test_rate_proficiency_happy_path(api_client, auth_headers, db_session):
    """PUT valid level → 200; user_skills + the caller's steps updated.

    Also proves the ladder update is per-user: another user's step for
    the same skill keeps its prior current_level.
    """
    skill_id, step_id = _rate_veteran_step(db_session)
    if skill_id is None:
        pytest.skip("no seeded veteran step with a skill link")

    other_step, _ = _second_user_step(db_session, api_client, skill_id)
    other_before = other_step.current_level

    response = api_client.put(
        f"/api/learning/skills/{skill_id}/proficiency",
        json={"level": 3}, headers=auth_headers)
    assert response.status_code == 200, response.text

    db_session.expire_all()
    vid = _veteran_id(db_session)
    us = db_session.query(UserSkill).filter_by(
        user_id=vid, skill_id=skill_id).first()
    assert us is not None
    assert us.proficiency_level == 3

    for s in _veteran_steps(db_session, skill_id):
        assert s.current_level == 3

    other_after = db_session.query(PathStep).filter_by(
        id=other_step.id).first()
    assert other_after.current_level == other_before


@pytest.mark.parametrize("level", [-1, 6])
def test_rate_proficiency_out_of_range(api_client, auth_headers, db_session,
                                       level):
    """Levels outside 0..5 → 400 (router range check)."""
    skill_id, _ = _rate_veteran_step(db_session)
    if skill_id is None:
        pytest.skip("no seeded veteran step with a skill link")
    response = api_client.put(
        f"/api/learning/skills/{skill_id}/proficiency",
        json={"level": level}, headers=auth_headers)
    assert response.status_code == 400


def test_rate_proficiency_unknown_skill(api_client, auth_headers):
    """Unknown skill id → 400."""
    response = api_client.put(
        "/api/learning/skills/9999999/proficiency",
        json={"level": 3}, headers=auth_headers)
    assert response.status_code == 400


def test_rate_proficiency_writes_audit(api_client, auth_headers, db_session):
    """rate.proficiency.set row written with actor + entity + level."""
    skill_id, _ = _rate_veteran_step(db_session)
    if skill_id is None:
        pytest.skip("no seeded veteran step with a skill link")

    response = api_client.put(
        f"/api/learning/skills/{skill_id}/proficiency",
        json={"level": 4}, headers=auth_headers)
    assert response.status_code == 200, response.text

    audit = db_session.query(ActivityLog).filter_by(
        action="rate.proficiency.set").order_by(
        ActivityLog.id.desc()).first()
    assert audit is not None
    assert audit.user_id == _veteran_id(db_session)
    assert audit.entity_type == "skill"
    assert int(audit.entity_id) == skill_id
    assert audit.data["level"] == 4
