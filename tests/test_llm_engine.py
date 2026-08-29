"""tests/test_llm_engine.py — guard rails around the GGUF singleton."""
import pytest

from backend.services import llm_engine, settings_service


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
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: False)
    assert llm_engine.available() is False


def test_complete_raises_when_model_missing(monkeypatch):
    """Missing GGUF file → LLMUnavailable on complete.

    Proves graceful degradation contract (spec: Failure Handling).
    String-target patching avoids mutating shared module refs and works
    regardless of ambient AI_ENABLED left cached by test_ai_config.
    """
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
    monkeypatch.setattr("backend.config.app_settings.AI_MODEL_PATH",
                        "/nonexistent/model.gguf")
    with pytest.raises(llm_engine.LLMUnavailable):
        llm_engine.complete("ping", max_tokens=8)


def test_load_failure_latches(monkeypatch):
    """A failed load marks the engine failed instead of retry-storming.

    Consumed by warmup()/health(); reset_for_tests clears it.
    """
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
    monkeypatch.setattr("backend.config.app_settings.AI_MODEL_PATH",
                        "/nonexistent/model.gguf")
    assert llm_engine.warmup() is False
    assert llm_engine._load_failed is True
    h = llm_engine.health()
    assert h["available"] is False and h["loaded"] is False


def test_fit_layers_explicit_override_wins():
    """requested>=0 is returned unchanged (user pinned the value)."""
    assert llm_engine._fit_layers(0, 0, 12) == 12
    assert llm_engine._fit_layers(3800, 2643853856, 0) == 0


def test_fit_layers_cpu_only_when_no_vram():
    """No detected VRAM (probe fails) → 0 layers, never OOM."""
    assert llm_engine._fit_layers(0, 2643853856, -1) == 0
    assert llm_engine._fit_layers(1000, 2643853856, -1) == 0


def test_fit_layers_sizes_to_free_vram():
    """Small-GPU default (-1) offloads a VRAM-sized fraction of layers."""
    assert 0 < llm_engine._fit_layers(3800, 2643853856, -1) <= \
        llm_engine._TOTAL_LAYERS
