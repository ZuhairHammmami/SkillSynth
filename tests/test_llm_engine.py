"""tests/test_llm_engine.py — guard rails around the GGUF singleton."""
import pytest

from backend.services import llm_engine


@pytest.fixture(autouse=True)
def _fresh_engine():
    """Reset singleton state around each engine test.

    Keeps module-level _llm/_load_failed latches from leaking.
    """
    llm_engine.reset_for_tests()
    yield
    llm_engine.reset_for_tests()


def test_unavailable_when_disabled(monkeypatch):
    """Disabled flag short-circuits availability.

    Consumed by pipeline/router gates; keeps CI hermetic.
    """
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", False)
    assert llm_engine.available() is False


def test_complete_raises_when_model_missing(monkeypatch):
    """Missing GGUF file → LLMUnavailable on complete.

    Proves graceful degradation contract (spec: Failure Handling).
    String-target patching avoids mutating shared module refs and works
    regardless of ambient AI_ENABLED left cached by test_ai_config.
    """
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr("backend.config.app_settings.AI_MODEL_PATH",
                        "/nonexistent/model.gguf")
    with pytest.raises(llm_engine.LLMUnavailable):
        llm_engine.complete("ping", max_tokens=8)


def test_load_failure_latches(monkeypatch):
    """A failed load marks the engine failed instead of retry-storming.

    Consumed by warmup()/health(); reset_for_tests clears it.
    """
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr("backend.config.app_settings.AI_MODEL_PATH",
                        "/nonexistent/model.gguf")
    assert llm_engine.warmup() is False
    assert llm_engine._load_failed is True
    h = llm_engine.health()
    assert h["available"] is False and h["loaded"] is False
