"""Tests for the leveled step-test service (tasks 2.4 / 2.5 / 2.6 / 2.8)."""

import types
from unittest import mock

from backend.entities.catalog import Skill
from backend.entities.identity import User
from backend.entities.learning import Path, PathStep
from backend.repositories import assess_repository as arepo
from backend.services import assess_service, llm_pipeline
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


def _set_proficiency(db_session, user_id, skill_id, level):
    """Pin the user's proficiency_level for a skill (persisted)."""
    arepo.upsert_user_skill(db_session, user_id, skill_id, level)
    db_session.commit()


def _fake_review(correct, total, difficulty, attempt_no, current_level):
    """Stand-in for the bounded-autonomy verdict (Task 2.6 seam).

    Simulates a high-confidence model: +1 on pass, -1 on fail, clamped 0..5,
    mirroring llm_pipeline.review_level without requiring the LLM engine.
    """
    passed = (correct / total) >= st._PASS_THRESHOLD if total else False
    delta = 1 if passed else -1
    target = current_level + delta
    final = max(0, min(5, target))
    return {"delta": delta, "confidence": "high", "rationale": "test",
            "applied": target != current_level, "final_level": final}


def _grade_with(db_session, user_id, step, correct=True):
    """Generate a seeded test for step, then grade all-correct/all-wrong."""
    payload, err, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", ai_enabled=False)
    assert err is None, err
    answers = {
        str(q["id"]): (q["correct_index"] if correct
                       else (q["correct_index"] + 1) % 4)
        for q in payload["questions"]}
    result, gerr, _ = st.grade_step_test(
        db_session, user_id, step.id,
        {"assessment_id": payload["assessment_id"], "answers": answers},
        locale="en")
    assert gerr is None, gerr
    return result


def test_generate_step_test_level1_uses_seeded_topics(db_session, monkeypatch):
    """Level 1 must use the skill/step objectives (no AI, no level pattern)."""
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    ai_topics = mock.MagicMock()
    monkeypatch.setattr(llm_pipeline, "generate_skill_topics", ai_topics)
    payload, err, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", level=1, ai_enabled=False)
    assert err is None, err
    assert payload["questions"], "seeded questions required"
    assert ai_topics.call_count == 0, "level 1 must not consult AI topics"
    assert payload["topics"] == st._topics_for(skill, step)
    assert not any("(level " in t for t in payload["topics"])


def test_generate_step_test_high_level_ai_disabled_seeded_fallback(
        db_session, monkeypatch):
    """Level > 1 with AI disabled must return a deterministic seeded fallback.

    Mocks llm_pipeline._engine_available to False and forces AI_ENABLED off so
    the test never touches the LLM; the payload must still be well-formed and
    reproducible.
    """
    monkeypatch.setattr(st.settings, "AI_ENABLED", False)
    monkeypatch.setattr(llm_pipeline, "_engine_available", lambda: False)
    ai_quiz = mock.MagicMock(side_effect=AssertionError("AI must not run"))
    monkeypatch.setattr(llm_pipeline, "generate_skill_quiz", ai_quiz)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=3)
    payload, err, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", level=3)
    assert err is None, err
    assert payload["questions"], "seeded fallback must yield questions"
    assert payload["assessment_id"] is not None
    assert all("(level 3)" in t for t in payload["topics"]), payload["topics"]
    again, _, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", level=3)
    assert again["topics"] == payload["topics"]
    assert again["questions"] == payload["questions"]


def test_grade_failing_lowers_level(db_session, monkeypatch):
    """A failing attempt lowers the level by one (seam-driven verdict)."""
    monkeypatch.setattr(assess_service, "review_level", _fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 3)
    result = _grade_with(db_session, user_id, step, correct=False)
    assert result["passed"] is False
    assert result["next_level"] == 2, "fail must lower level by 1"
    assert result["level_passed"] is False
    assert st._proficiency(db_session, user_id, skill.id) == 2


def test_grade_failing_holds_at_floor(db_session, monkeypatch):
    """A failing attempt at the floor (0) holds rather than going negative."""
    monkeypatch.setattr(assess_service, "review_level", _fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 0)
    result = _grade_with(db_session, user_id, step, correct=False)
    assert result["next_level"] == 0, "fail at floor must hold at 0"
    assert st._proficiency(db_session, user_id, skill.id) == 0


def test_grade_pass_below_top_raises_level(db_session, monkeypatch):
    """A passing attempt below the top level raises the level by one."""
    monkeypatch.setattr(assess_service, "review_level", _fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 2)
    result = _grade_with(db_session, user_id, step, correct=True)
    assert result["passed"] is True
    assert result["next_level"] == 3, "pass below top must raise by 1"
    assert result["level_passed"] is True
    assert st._proficiency(db_session, user_id, skill.id) == 3


def test_grade_pass_at_top_holds_level(db_session, monkeypatch):
    """A passing attempt at the top level (5) holds the level, no overflow."""
    monkeypatch.setattr(assess_service, "review_level", _fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 5)
    result = _grade_with(db_session, user_id, step, correct=True)
    assert result["passed"] is True
    assert result["next_level"] == 5, "pass at top must hold at 5"
    assert result["level_passed"] is True
    assert st._proficiency(db_session, user_id, skill.id) == 5
