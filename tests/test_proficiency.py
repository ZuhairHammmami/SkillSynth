"""tests/test_proficiency.py — PUT /api/learning/skills/{id}/proficiency."""
import pytest

from backend.entities.engagement import ActivityLog
from backend.entities.identity import User
from backend.entities.learning import Path, PathStep, UserSkill

_TOUCHED = set()


def _veteran_id(db_session):
    """id of the seeded veteran account (authed by auth_headers)."""
    return db_session.query(User).filter_by(
        email="veteran@skillsynth.io").first().id


@pytest.fixture(autouse=True)
def purge_proficiency_rows(db_session):
    """Delete this module's authored rows so pinned seed counts stay green.

    Removes the rate.proficiency.set activity rows and the UserSkill
    rows the route wrote for the authed account on the skills it touched
    (tracked per call; seeded proficiency rows for other skills stay).
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
    _TOUCHED.clear()
    db_session.commit()


def _rate_veteran_step(db_session):
    """(skill_id, step_id) of a seeded veteran step, else (None, None).

    The route updates every PathStep of a skill regardless of owner, so
    any veteran step with a skill link lets us assert persistence.
    """
    step = (db_session.query(PathStep)
            .join(Path, PathStep.path_id == Path.id)
            .filter(Path.user_id == _veteran_id(db_session),
                    PathStep.skill_id.isnot(None))
            .first())
    if step is None:
        return None, None
    _TOUCHED.add(step.skill_id)
    return step.skill_id, step.id


def test_rate_proficiency_happy_path(api_client, auth_headers, db_session):
    """PUT valid level → 200; user_skills + path_steps.current_level set."""
    skill_id, step_id = _rate_veteran_step(db_session)
    if skill_id is None:
        pytest.skip("no seeded veteran step with a skill link")

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
    assert db_session.query(PathStep).filter_by(
        id=step_id).first().current_level == 3
    for s in db_session.query(PathStep).filter(
            PathStep.skill_id == skill_id).all():
        assert s.current_level == 3


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
