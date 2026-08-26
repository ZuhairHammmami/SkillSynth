"""Tests for `skillsynth doctor --strict` exit codes (D2)."""

import argparse

from backend.cli import _cmd_doctor


def test_strict_fails_when_ai_enabled_and_model_missing(monkeypatch):
    """Strict doctor exits 1 when AI is enabled but the model file is absent."""
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(
        "backend.config.app_settings.AI_MODEL_PATH",
        "src/data/does-not-exist.gguf")
    assert _cmd_doctor(argparse.Namespace(strict=True)) == 1


def test_strict_passes_when_ai_disabled(monkeypatch):
    """Strict doctor exits 0 when AI is disabled despite a missing model file."""
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", False)
    assert _cmd_doctor(argparse.Namespace(strict=True)) == 0
