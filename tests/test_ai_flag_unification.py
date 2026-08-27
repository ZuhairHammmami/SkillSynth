"""Unification test: AI flag must follow the runtime settings store.

Verifies that step-test gating and skill-topic generation read
settings_service.is_ai_enabled() rather than the env constant, without
invoking the real LLM model.
"""

import pytest

from backend.services import settings_service, step_test_service, llm_pipeline


@pytest.fixture
def ai_flag():
    """Snapshot and restore the runtime AI flag around each test."""
    original = settings_service.is_ai_enabled()
    try:
        yield
    finally:
        settings_service.set_ai_enabled(original)


def test_step_test_gate_off_when_flag_off(ai_flag):
    """AI disabled in settings store must make _ai_active() False."""
    settings_service.set_ai_enabled(False)
    assert step_test_service._ai_active() is False


def test_topic_generation_falls_back_when_flag_off(ai_flag, monkeypatch):
    """Disabled flag yields the deterministic seeded topics, no LLM used."""
    settings_service.set_ai_enabled(False)
    monkeypatch.setattr(llm_pipeline, "_engine_available", lambda: False)
    assert (llm_pipeline.generate_skill_topics("X", 1)
            == llm_pipeline._seeded_topics("X", 1))


def test_step_test_gate_on_when_flag_on(ai_flag):
    """Enabled runtime flag must make _ai_active() True (gate follows toggle)."""
    settings_service.set_ai_enabled(True)
    assert step_test_service._ai_active() is True
