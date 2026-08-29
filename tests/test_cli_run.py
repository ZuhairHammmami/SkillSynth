"""tests.test_cli_run — unit tests for the OS-aware cross-platform run helpers.

Pure tests that never start servers; they only exercise _pnpm_bin and
_terminate_session on the current platform. Imported by pytest via the
backend.cli module; PYTHONPATH=src is required (set by the skillsynth test
runner and the repo's pytest invocation).
"""

import subprocess

from backend.cli import _pnpm_bin, _terminate_session


def test_pnpm_bin_returns_string_or_none():
    """Assert _pnpm_bin resolves to a path or None without raising."""
    result = _pnpm_bin()
    assert result is None or isinstance(result, str) and len(result) > 0


def test_terminate_finished_process_does_not_raise():
    """Assert _terminate_session on a finished proc is exception-safe."""
    proc = subprocess.Popen(["true"])
    proc.wait()
    try:
        _terminate_session(proc)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise AssertionError(f"_terminate_session raised on finished proc: {exc}")
