"""Tests for the leveled step-test service (tasks 2.4 / 2.5 / 2.6 / 2.8).

Covers the bank-first-by-default generation (deterministic, no LLM on the
request path), synchronous deterministic grading, and the async bounded-AI
review (proficiency_adjusted + ai_step_diagnostic via step_jobs).
"""

import types
from unittest import mock

import pytest

from backend.entities.catalog import Skill
from backend.entities.identity import User
from backend.entities.learning import Path, PathStep
from backend.events import publisher
from backend.repositories import assess_repository as arepo
from backend.services import assess_service, llm_pipeline, settings_service
from backend.services import step_test_service as st


@pytest.fixture(autouse=True)
def _clear_review_audits(db_session):
    """Drop ai_proficiency_review rows so the async-review tests are isolated."""
    from backend.entities.engagement import ActivityLog
    db_session.query(ActivityLog).filter(
        ActivityLog.action == "ai_proficiency_review").delete(
        synchronize_session=False)
    db_session.commit()
    yield


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


def _no_llm(monkeypatch):
    """Bomb if the request path ever touches the LLM (fast test gate)."""
    monkeypatch.setattr(llm_pipeline, "generate_skill_topics",
                        mock.MagicMock(
                            side_effect=AssertionError("LLM topics must not run")))
    monkeypatch.setattr(llm_pipeline, "generate_skill_quiz",
                        mock.MagicMock(
                            side_effect=AssertionError("LLM quiz must not run")))
    monkeypatch.setattr(llm_pipeline, "analyze_diagnostic",
                        mock.MagicMock(
                            side_effect=AssertionError("LLM diag must not run")))


def _disable_review(monkeypatch):
    """Keep deterministic grading green by never spawning a real review."""
    monkeypatch.setattr(st, "_spawn_review", lambda fn: None)
    monkeypatch.setattr(llm_pipeline, "_engine_available", lambda: False)


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


def test_generate_bank_first_no_llm_on_request_path(db_session, monkeypatch):
    """Open must come from the seeded bank, instantly, without any LLM call."""
    _no_llm(monkeypatch)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=3)
    payload, err, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", level=3,
        enrich=True)  # enrich requested but AI gate off → still bank-only
    assert err is None, err
    assert payload["questions"], "seeded bank must supply questions"
    assert payload["assessment_id"] is not None
    assert all("(level 3)" in t for t in payload["topics"]), payload["topics"]
    assert all(q.get("correct_index") is not None for q in payload["questions"])


def test_grade_failing_attempt_no_nameerror_and_holds_level(db_session,
                                                            monkeypatch):
    """Failing grade with AI off must not raise; deterministic level lands."""
    _disable_review(monkeypatch)
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
    assert result["next_level"] == max(
        0, min(5, round(result["correct"] / result["total"] * 5)))
    assert result["next_level"] <= before + 1
    assert result["level_passed"] is True or result["next_level"] <= before


def test_grade_passing_attempt_completes_step(db_session, monkeypatch):
    """All-correct grade must pass deterministically and complete the step."""
    _disable_review(monkeypatch)
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

    Forces the runtime AI flag off so the test never touches the LLM; the
    payload must still be well-formed and reproducible.
    """
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: False)
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


def _set_proficiency(db_session, user_id, skill_id, level):
    """Pin the user's proficiency_level for a skill (persisted)."""
    arepo.upsert_user_skill(db_session, user_id, skill_id, level)
    db_session.commit()


def _grade(db_session, user_id, step, correct=True):
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


def _review_env(monkeypatch, review_fn):
    """Enable AI + run reviews inline and capture SSE; returns `sent` list.

    Patches the seams the bounded review depends on so no real model loads:
    review_level is faked, _engine_ready forced on, and llm_pipeline's own
    gate stays off so the diagnostic narrative resolves harmlessly.
    """
    sent = []
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
    monkeypatch.setattr(st, "_engine_ready", lambda: True)
    monkeypatch.setattr(llm_pipeline, "_engine_available", lambda: False)
    monkeypatch.setattr(assess_service, "review_level", review_fn)
    monkeypatch.setattr(st, "_spawn_review", lambda fn: fn())
    monkeypatch.setattr(publisher, "send_event",
                        lambda uid, t, d=None: sent.append((uid, t, d)))
    return sent


def test_grade_applies_high_confidence_review(db_session, monkeypatch):
    """Async review applies +1; audit row + proficiency_adjusted SSE land."""
    from backend.entities.engagement import ActivityLog

    def fake_review(correct, total, difficulty, attempt_no, current_level):
        return {"delta": 1, "confidence": "high", "rationale": "solid",
                "applied": True, "final_level": min(5, current_level + 1)}

    sent = _review_env(monkeypatch, fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 2)
    payload, err, _ = st.generate_step_test(
        db_session, user_id, step.id, locale="en", ai_enabled=False)
    assert err is None, err
    questions = payload["questions"]
    half = len(questions) // 2 or 1
    answers = {}
    for i, q in enumerate(questions):
        answers[str(q["id"])] = (q["correct_index"] if i < half
                                 else (q["correct_index"] + 1) % 4)
    result, gerr, _ = st.grade_step_test(
        db_session, user_id, step.id,
        {"assessment_id": payload["assessment_id"], "answers": answers},
        locale="en")
    assert gerr is None, gerr
    formula = round(result["correct"] / result["total"] * 5)
    db_session.expire_all()
    assert result["next_level"] == formula
    assert st._proficiency(db_session, user_id, skill.id) == min(5, formula + 1)
    audit = db_session.query(ActivityLog).filter_by(
        action="ai_proficiency_review").order_by(
        ActivityLog.id.desc()).first()
    assert audit is not None
    assert audit.user_id == user_id
    assert audit.entity_type == "skill"
    assert audit.data["delta"] == 1
    assert any(t == "proficiency_adjusted"
               for _, t, _ in sent), sent


def test_grade_low_confidence_keeps_formula_level(db_session, monkeypatch):
    """applied False → deterministic formula level stands, no audit row."""
    from backend.entities.engagement import ActivityLog

    def fake_review(correct, total, difficulty, attempt_no, current_level):
        return {"delta": 1, "confidence": "low", "rationale": "unsure",
                "applied": False, "final_level": current_level}

    _review_env(monkeypatch, fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 2)
    result = _grade(db_session, user_id, step, correct=True)
    db_session.expire_all()
    assert result["next_level"] == st._proficiency(db_session, user_id, skill.id)
    assert db_session.query(ActivityLog).filter_by(
        action="ai_proficiency_review").count() == 0


def test_grade_review_skipped_when_engine_unready(db_session, monkeypatch):
    """Engine not ready ⇒ review_level never invoked; formula level stands."""
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
    monkeypatch.setattr(st, "_engine_ready", lambda: False)
    boom = mock.MagicMock(side_effect=AssertionError("review must not run"))
    monkeypatch.setattr(assess_service, "review_level", boom)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 2)
    result = _grade(db_session, user_id, step, correct=False)
    assert result["next_level"] == 0
    assert st._proficiency(db_session, user_id, skill.id) == 0


def test_grade_diagnostic_emits_ai_step_diagnostic(db_session, monkeypatch):
    """Background review emits ai_step_diagnostic with refined weak points."""
    from backend.entities.engagement import ActivityLog

    def fake_review(correct, total, difficulty, attempt_no, current_level):
        return {"delta": 0, "confidence": "low", "rationale": "ok",
                "applied": False, "final_level": current_level}

    canned = {"summary": "s", "strengths": [], "weaknesses":
              [{"focus": "Topic A"}], "recommended_focus": ["Topic B"],
              "next_steps": ""}
    monkeypatch.setattr(llm_pipeline, "analyze_diagnostic",
                        lambda *a, **k: dict(canned))
    sent = _review_env(monkeypatch, fake_review)
    user_id = _veteran_id(db_session)
    skill = db_session.query(Skill).first()
    step = _make_step(db_session, user_id, skill, level=1)
    _set_proficiency(db_session, user_id, skill.id, 2)
    _grade(db_session, user_id, step, correct=False)
    diag = [d for _, t, d in sent if t == "ai_step_diagnostic"]
    assert diag, "ai_step_diagnostic must be emitted"
    assert diag[0]["weak_points"] == ["Topic A"]
    assert diag[0]["topics_to_master"] == ["Topic A", "Topic B"]
