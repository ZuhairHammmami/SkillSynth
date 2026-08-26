"""backend.cli — skillsynth console entrypoint (run/seed/test/schema/doctor).

Installed as the `skillsynth` console script via pyproject [project.scripts]
and wrapped by ./skillsynth (bash shim) plus run.py (legacy launcher).
Subcommands delegate to uvicorn (`run`), seed_v3.seed (`seed`), a pytest
subprocess (`test`), tools/verify_schema.py (`schema`), local health probes
(`doctor`) and package metadata (`version`). See docs/25-cli/INDEX.md.
"""

import argparse
import importlib.metadata
import os
import runpy
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
SRC_PATH = os.path.join(BASE_DIR, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

REQUIRED_DEPS = ("fastapi", "sqlalchemy", "uvicorn")


def main(argv=None):
    """Parse argv, dispatch to one subcommand handler, return its exit code.

    Entry point of the `skillsynth` console script, the ./skillsynth shim,
    run.py, and tests/test_cli.py; dispatches to _cmd_run/_cmd_seed/_cmd_test/
    _cmd_schema/_cmd_doctor/_cmd_version. `test` short-circuits before
    argparse so dashed pytest flags (-k ...) pass through; argparse exits
    (--help, unknown command) become status codes.
    """
    tokens = list(sys.argv[1:]) if argv is None else list(argv)
    if tokens and tokens[0] == "test":
        return int(_cmd_test(argparse.Namespace(pytest_args=tokens[1:])))
    parser = _build_parser()
    try:
        args = parser.parse_args(tokens)
    except SystemExit as exc:
        return int(exc.code or 0)
    return int(args.func(args))


def _build_parser():
    """Build the argparse tree wiring every subcommand to its handler.

    Called once by main; handlers are _cmd_run/_cmd_seed/_cmd_test/
    _cmd_schema/_cmd_doctor/_cmd_version. Returns the configured parser.
    """
    parser = argparse.ArgumentParser(
        prog="skillsynth", description="SkillSynth console entrypoint")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p_run = sub.add_parser("run", help="serve backend.main:app via uvicorn")
    p_run.add_argument("--host", default=None, help="overrides HOST env")
    p_run.add_argument("--port", type=int, default=None, help="overrides PORT env")
    p_run.add_argument("--dev", action="store_true", help="force autoreload")
    p_run.set_defaults(func=_cmd_run)

    p_seed = sub.add_parser("seed", help="run seed_v3 against --db")
    p_seed.add_argument("--db", default="skillsynth.db",
                        help="target SQLite file (default skillsynth.db)")
    p_seed.set_defaults(func=_cmd_seed)

    p_test = sub.add_parser("test", help="run pytest tests/ [args...]")
    p_test.add_argument("pytest_args", nargs="*", help="pass-through args")
    p_test.set_defaults(func=_cmd_test)

    sub.add_parser(
        "schema",
        help="verify canonical DDL vs ORM (SCHEMA MATCH)").set_defaults(
        func=_cmd_schema)
    p_doc = sub.add_parser("doctor", help="environment health table")
    p_doc.add_argument("--strict", action="store_true",
                       help="exit 1 when a required check fails")
    p_doc.set_defaults(func=_cmd_doctor)

    p_ver = sub.add_parser("version", help="print name + version").set_defaults(
        func=_cmd_version)
    return parser


def _cmd_run(args):
    """Serve backend.main:app with uvicorn, mirroring legacy run.py exactly.

    Invoked by main via `skillsynth run`; loads .env, injects src/ onto the
    path, resolves host/port from flags over HOST/PORT env defaults, enables
    reload when --dev or MODE=dev, then blocks until shutdown. Returns 0.
    """
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["PYTHONPATH"] = SRC_PATH
    host = args.host or os.getenv("HOST", "127.0.0.1")
    port = int(args.port if args.port is not None else os.getenv("PORT", "8000"))
    reload_on = bool(args.dev) or os.getenv("MODE", "prod").lower() == "dev"
    import uvicorn
    uvicorn.run("backend.main:app", host=host, port=port,
                reload=reload_on, log_level="info")
    return 0


def _cmd_seed(args):
    """Seed the SQLite file at --db by driving seed_v3's injection seam.

    Invoked by main via `skillsynth seed`; executes the real seed_v3.py with
    runpy under a non-__main__ name (its auto-run never fires), then calls its
    documented seed(engine, session_factory) seam bound to an isolated engine
    at the requested path — the dev database is never opened when --db points
    elsewhere. Returns 0, or the seed FK-gate exit code on failure.
    """
    db_path = os.path.abspath(args.db)
    namespace = runpy.run_path(
        os.path.join(BASE_DIR, "seed_v3.py"), run_name="skillsynth_cli_seed")
    engine, factory = _make_seed_engine(db_path)
    try:
        namespace["seed"](engine=engine, session_factory=factory)
    except SystemExit as exc:
        return int(exc.code or 1)
    finally:
        engine.dispose()
    return 0


def _make_seed_engine(db_path):
    """Build an FK-enforced engine + session factory bound to db_path.

    Called by _cmd_seed; mirrors the dev pragmas of backend.database
    (foreign_keys/WAL/synchronous) so seeded data gets the same guarantees
    as the running app. Returns an (engine, sessionmaker) tuple.
    """
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def apply_pragmas(dbapi_connection, connection_record):
        """Apply dev-mode SQLite pragmas on every new connection."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return engine, sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _cmd_test(args):
    """Run the pytest suite in a subprocess and pass its exit code through.

    Invoked by main via `skillsynth test [args...]`; spawns
    [sys.executable, -m, pytest, tests/, *args] with cwd at repo root and
    PYTHONPATH=src. Returns the subprocess return code unchanged.
    """
    env = dict(os.environ, PYTHONPATH=SRC_PATH)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", *args.pytest_args],
        cwd=BASE_DIR, env=env, check=False)
    return proc.returncode


def _cmd_schema(args):
    """Execute tools/verify_schema.py and pass through its exit status.

    Invoked by main via `skillsynth schema`; runpy executes the verifier with
    __main__ semantics so its sys.exit becomes our process exit code.
    Returns 0 on SCHEMA MATCH, 1 on drift.
    """
    try:
        runpy.run_path(
            os.path.join(BASE_DIR, "tools", "verify_schema.py"),
            run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


def _cmd_doctor(args):
    """Print the environment health table and compute the exit code.

    Invoked by main via `skillsynth doctor [--strict]`; gathers probe rows
    from _doctor_rows (llama_cpp imported only when AI_ENABLED=true), prints
    them aligned, and returns 1 solely under --strict with a failed required
    row — otherwise always 0.
    """
    rows = _doctor_rows()
    width = max(len(row[0]) for row in rows) + 2
    for label, ok, required, detail in rows:
        status = "OK" if ok else ("FAIL" if required else "WARN")
        print(f"{status:<5} {label:<{width}}{detail}")
    strict_failed = any(not ok and required for _, ok, required, _ in rows)
    if args.strict and strict_failed:
        print("doctor: strict check FAILED")
        return 1
    return 0


def _doctor_rows():
    """Collect (label, ok, required, detail) probe rows for the doctor table.

    Called by _cmd_doctor; probes required imports (_check_deps), SS-AI
    configuration and artifacts (_check_ai), and the dev database file.
    Returns the ordered row list.
    """
    dep_ok, dep_detail = _check_deps()
    rows = [("deps fastapi/sqlalchemy/uvicorn", dep_ok, True, dep_detail)]
    rows.extend(_check_ai())
    db_path = os.path.join(BASE_DIR, "skillsynth.db")
    rows.append(
        ("db skillsynth.db", os.path.exists(db_path), True,
         f"{_fmt_size(db_path)}, {db_path}" if os.path.exists(db_path)
         else "missing — run seed"))
    return rows


def _check_deps():
    """Probe the three hard runtime dependencies by importing them (_doctor_rows)."""
    missing = []
    for module in REQUIRED_DEPS:
        try:
            __import__(module)
        except ImportError as exc:
            missing.append(f"{module} ({exc})")
    return not missing, "; ".join(missing) or "all importable"


def _check_ai():
    """Probe SS-AI flag, optional llama_cpp, and the GGUF model file.

    Called by _doctor_rows; imports config/app_settings guarded so a broken
    environment still yields rows instead of crashing doctor, and imports
    llama_cpp only when AI_ENABLED=true. Model/dependency rows are required
    only while AI is enabled. Returns the row list.
    """
    try:
        from backend.config.app_settings import AI_ENABLED, AI_MODEL_PATH
    except Exception as exc:
        return [("ai settings", False, False, f"app_settings unusable ({exc})")]
    rows = [("ai AI_ENABLED", True, False,
             "true" if AI_ENABLED else "false")]
    model_path = AI_MODEL_PATH
    if not os.path.isabs(model_path):
        model_path = os.path.join(BASE_DIR, model_path)
    rows.append(
        ("ai model file", os.path.exists(model_path), AI_ENABLED,
         f"{_fmt_size(model_path)}, {model_path}" if os.path.exists(model_path)
         else f"missing at {model_path}"))
    if AI_ENABLED:
        try:
            import llama_cpp  # noqa: F401
            rows.append(("ai llama_cpp", True, True, "importable"))
        except ImportError as exc:
            rows.append(("ai llama_cpp", False, True,
                         f"not importable ({exc})"))
    else:
        rows.append(("ai llama_cpp", True, False, "skipped (AI_ENABLED=false)"))
    return rows


def _fmt_size(path):
    """Return a human-readable MiB size string for an existing file.

    Called by _doctor_rows/_check_ai; returns "n/a" for missing paths.
    """
    if not os.path.exists(path):
        return "n/a"
    return f"{os.path.getsize(path) / (1024 * 1024):.1f} MiB"


def _cmd_version(args):
    """Print the package identity line for main (`skillsynth version`); returns 0.

    Prefers importlib.metadata, falling back to pyproject.toml when the
    distribution is absent.
    """
    try:
        version = importlib.metadata.version("skillsynth")
    except importlib.metadata.PackageNotFoundError:
        version = _version_from_pyproject()
    print(f"skillsynth {version}")
    return 0


def _version_from_pyproject():
    """Read the version from pyproject.toml for _cmd_version; "unknown" on error."""
    import tomllib
    try:
        with open(os.path.join(BASE_DIR, "pyproject.toml"), "rb") as handle:
            return tomllib.load(handle)["project"]["version"]
    except Exception:
        return "unknown"
