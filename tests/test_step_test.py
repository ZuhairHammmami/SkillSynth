"""Tests for the leveled step-test service (tasks 2.4 / 2.5 / 2.8 fixes)."""

import types

from backend.entities.catalog import Skill
from backend.entities.identity import User
from backend.entities.learning import Path, PathStep
from backend.services import step_test_service as st


def _make_step(db, user_id, skill, level=1):
    """Create a path + step owned by user_id for the given skill."""
    path = Path(user_id=user_id, title="t", total_estimated_hours=1,
                total_estimated_weeks=1)
    db.add(path)
    db.commit()
    step = PathStep(path_id=path.id, skill_id=skill.id, position=1,
                    title="s", current_level=level)
    db.add(step)
    db.commit()
    return step


def _veteran_id(db):
    """Return the seeded veteran user id (has a known login)."""
    return db.query(User).filter_by(
        email="veteran@skillsynth.io").first().id


def test_compute_effective_difficulty_adapts_to_recent_result():
    """Failed last_result lowers difficulty; passed raises it (clamped)."""
    skill = types.SimpleNamespace(difficulty_level=2)
    topics = ["a", "b"]
    baseline = st.compute_effective_difficulty(skill, None, topics)
    assert baseline == 4  # base 2 + bonus 2 (both mastered)
    failed = st.compute_effective_difficulty(
        skill, None, topics, last_result={"passed": False})
    assert failed == 3, "failed attempt must lower difficulty by 1"
    passed = st.compute_effective_difficulty(
        skill, None, topics, last_result={"passed": True})
    assert passed == 5, "passed attempt must raise difficulty (cap 5)"
    floor = st.compute_effective_difficulty(
        types.SimpleNamespace(difficulty_level=1), None, [], last_result=False)
    assert floor == 1, "difficulty must floor at 1 on repeated failure"
    ceil = st.compute_effective_difficulty(
        types.SimpleNamespace(difficulty_level=5), None, [], last_result=True)
    assert ceil == 5, "difficulty must cap at 5 on repeated pass"


def test_grade_failing_attempt_no_nameerror_and_holds_level(db_session):
    """Failing grade with AI disabled must not raise and next_level holds."""
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=2)
    payload, err, status = st.generate_step_test(
        db_session, user_id, step.id, locale="en", ai_enabled=False)
    assert err is None, err
    questions = payload["questions"]
    assert questions, "expected seeded questions"
    correct = questions[0]["correct_index"]
    wrong = (correct + 1) % 4
    answers = {str(q["id"]): wrong for q in questions}
    before = st._proficiency(db_session, user_id, skill.id)
    result, gerr, _ = st.grade_step_test(
        db_session, user_id, step.id,
        {"assessment_id": payload["assessment_id"], "answers": answers},
        locale="en")
    assert gerr is None, gerr
    assert result["next_level"] <= before + 1
    assert result["level_passed"] is True or result["next_level"] <= before


def test_grade_passing_attempt_completes_step(db_session):
    """All-correct grade must pass and complete the step."""
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    payload, err, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", ai_enabled=False)
    assert err is None, err
    answers = {str(q["id"]): q["correct_index"]
               for q in payload["questions"]}
    result, gerr, _ = st.grade_step_test(
        db_session, user_id, step.id,
        {"assessment_id": payload["assessment_id"], "answers": answers},
        locale="en")
    assert gerr is None, gerr
    assert result["passed"] is True
    assert result["completed"] is True
