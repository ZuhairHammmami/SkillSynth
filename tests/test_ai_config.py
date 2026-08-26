"""tests/test_ai_config.py — AI settings block defaults."""
import importlib


def test_ai_defaults_off(monkeypatch):
    """AI flags default to disabled/CPU-safe values when env is absent.

    Called by nothing at runtime; guards Task-1 config contract consumed
    by llm_engine/routers so a bare checkout stays deterministic.
    """
    monkeypatch.delenv("AI_ENABLED", raising=False)
    monkeypatch.delenv("AI_MODEL_PATH", raising=False)
    monkeypatch.delenv("AI_REPEAT_PENALTY", raising=False)
    monkeypatch.delenv("AI_TOP_P", raising=False)
    import backend.config.app_settings as s
    m = importlib.reload(s)
    assert m.AI_ENABLED is False
    assert m.AI_MODEL_PATH.endswith(
        "Llama-3.2-3B-Instruct-uncensored.Q6_K.gguf")
    assert m.AI_N_CTX == 4096 and m.AI_TEMPERATURE == 0.3
    assert isinstance(m.AI_MAX_NEW_TOKENS, int)


def test_ai_anti_degeneration_defaults(monkeypatch):
    """Repeat-penalty/top-p sampling knobs default per task-13 budgets.

    Guards the anti-degeneration env contract consumed by
    llm_engine.complete against accidental default drift.
    """
    monkeypatch.delenv("AI_REPEAT_PENALTY", raising=False)
    monkeypatch.delenv("AI_TOP_P", raising=False)
    import backend.config.app_settings as s
    m = importlib.reload(s)
    assert m.AI_REPEAT_PENALTY == 1.15 and m.AI_TOP_P == 0.95


def test_ai_enabled_toggle(monkeypatch):
    """AI_ENABLED parses 'true' case-insensitively.

    Guards the env contract used by routers/ai.py gates. Reload mutates
    the SHARED module object, so the off state is reloaded back before
    returning — otherwise later suites inherit AI_ENABLED=True and the
    real engine answers their requests.
    """
    monkeypatch.setenv("AI_ENABLED", "TRUE")
    import backend.config.app_settings as s
    assert importlib.reload(s).AI_ENABLED is True
    monkeypatch.delenv("AI_ENABLED", raising=False)
    assert importlib.reload(s).AI_ENABLED is False
