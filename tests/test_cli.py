"""tests/test_cli.py — contract tests for the skillsynth console entrypoint."""

import hashlib
import os
import sqlite3
import sys

from backend import cli

REPO = cli.BASE_DIR


def test_version_returns_zero_and_prints_identity(capsys):
    """`skillsynth version` exits 0 and prints the package name."""
    assert cli.main(["version"]) == 0
    assert "skillsynth" in capsys.readouterr().out


def test_help_returns_zero_and_lists_all_commands(capsys):
    """`skillsynth --help` exits 0 and advertises every subcommand."""
    assert cli.main(["--help"]) == 0
    out = capsys.readouterr().out
    for word in ("run", "seed", "test", "schema", "doctor", "version"):
        assert word in out


def test_unknown_command_exit_code_is_two():
    """An unrecognized subcommand maps argparse's exit to 2."""
    assert cli.main(["definitely-not-a-command"]) == 2


def test_doctor_flag_off_always_zero(capsys):
    """`skillsynth doctor` without --strict exits 0 on a healthy dev box."""
    assert cli.main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "deps" in out and "db skillsynth.db" in out


def test_seed_db_target_creates_tables_without_touching_dev_db(tmp_path):
    """`skillsynth seed --db <tmp>` builds the 15 tables in the target file
    while the repo-root skillsynth.db stays byte-identical."""
    dev_db = os.path.join(REPO, "skillsynth.db")
    assert os.path.exists(dev_db), (
        f"dev database absent at {dev_db} — seed isolation cannot be "
        "verified silently; seed it first (seed_v3.py) and rerun")
    before = _digest(dev_db)
    target = tmp_path / "seeded.db"
    assert cli.main(["seed", "--db", str(target)]) == 0
    con = sqlite3.connect(str(target))
    tables = {row[0] for row in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert {"users", "skills", "categories", "paths", "user_skills"} <= tables
    assert _digest(dev_db) == before


def test_test_command_builds_pytest_argv(monkeypatch, tmp_path):
    """`skillsynth test [args...]` spawns pytest with tests/ prepended,
    cwd at repo root, PYTHONPATH=src, and passes the return code through."""
    captured = {}

    class Proc:
        returncode = 7

    def fake_run(argv, **kwargs):
        captured.update(argv=list(argv), kwargs=kwargs)
        return Proc()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    assert cli.main(["test", "-k", "auth"]) == 7
    assert captured["argv"][:4] == [sys.executable, "-m", "pytest", "tests/"]
    assert captured["argv"][4:] == ["-k", "auth"]
    assert captured["kwargs"]["cwd"] == REPO
    assert captured["kwargs"]["env"]["PYTHONPATH"] == cli.SRC_PATH


def test_schema_passes_through_exit_code(monkeypatch):
    """`skillsynth schema` returns verify_schema's own exit status (1 on drift)."""

    def fake_run_path(path, run_name):
        raise SystemExit(1)

    monkeypatch.setattr(cli.runpy, "run_path", fake_run_path)
    assert cli.main(["schema"]) == 1


def _digest(path):
    """Hash a file's bytes so a test can prove the dev DB stayed untouched."""
    with open(path, "rb") as handle:
        return hashlib.file_digest(handle, "md5").hexdigest()
