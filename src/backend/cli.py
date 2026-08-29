"""backend.cli — skillsynth console entrypoint (run/seed/test/schema/doctor/frontend/admin/verify).

Installed as the `skillsynth` console script via pyproject [project.scripts]
and wrapped by ./skillsynth (bash shim) plus run.py (legacy launcher).
Subcommands delegate to uvicorn (`run`), seed_v4.seed (`seed`), a pytest
subprocess (`test`), tools/verify_schema.py (`schema`), local health probes
(`doctor`), pnpm (`frontend`/`admin`) and the from-scratch `verify`
orchestrator (frontend+admin check/build, pytest, schema, doctor). See
docs/25-cli/INDEX.md.
"""

import argparse
import importlib.metadata
import os
import runpy
import shutil
import signal
import subprocess
import sys
import threading

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
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return int(args.func(args))


def _build_parser():
    """Build the argparse tree wiring every subcommand to its handler.

    Called once by main; handlers are _cmd_run/_cmd_seed/_cmd_test/
    _cmd_schema/_cmd_doctor/_cmd_version. Returns the configured parser.
    """
    parser = argparse.ArgumentParser(
        prog="skillsynth", description="SkillSynth console entrypoint")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p_run = sub.add_parser(
        "run", help="run the full project (backend + frontend + admin dev servers)")
    p_run.add_argument("--host", default=None, help="overrides HOST env")
    p_run.add_argument("--port", type=int, default=None, help="overrides PORT env")
    p_run.add_argument("--dev", action="store_true", help="force backend autoreload")
    p_run.add_argument("--skip-backend", action="store_true",
                       help="do not start the backend")
    p_run.add_argument("--skip-frontend", action="store_true",
                       help="do not start the frontend dev server")
    p_run.add_argument("--skip-admin", action="store_true",
                       help="do not start the admin dev server")
    p_run.set_defaults(func=_cmd_run)

    p_seed = sub.add_parser("seed", help="run seed_v4 against --db")
    p_seed.add_argument("--db", default=os.path.join(BASE_DIR, "skillsynth.db"),
                        help="target SQLite file (default <repo>/skillsynth.db)")
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

    p_fe = sub.add_parser(
        "frontend", help="pnpm check|build the student frontend")
    p_fe.add_argument("action", choices=["check", "build"],
                      help="svelte-check (type-check) or vite build")
    p_fe.add_argument("--clean-deps", action="store_true",
                      help="wipe node_modules + pnpm install before the action")
    p_fe.set_defaults(func=_cmd_frontend)

    p_ad = sub.add_parser("admin", help="pnpm check|build the admin app")
    p_ad.add_argument("action", choices=["check", "build"],
                      help="svelte-check (type-check) or vite build")
    p_ad.add_argument("--clean-deps", action="store_true",
                      help="wipe node_modules + pnpm install before the action")
    p_ad.set_defaults(func=_cmd_admin)

    p_v = sub.add_parser(
        "verify", help="full from-scratch verification: check+build both apps, "
                       "pytest, schema, doctor")
    p_v.add_argument(
        "--clean-deps", action="store_true",
        help="wipe + reinstall node_modules in both apps before building")
    p_v.set_defaults(func=_cmd_verify)

    p_ver = sub.add_parser("version", help="print name + version").set_defaults(
        func=_cmd_version)
    return parser


def _cmd_run(args):
    """Launch the full project and block until interrupted.

    Invoked by main via `skillsynth run`; dependencies imported locally are
    dotenv (load_dotenv) plus the spawn/supervise helpers. Implementation:
    loads .env, resolves the backend host/port, then spawns three managed
    child processes — the backend (uvicorn) plus the frontend and admin
    Next.js dev servers — each in its own session so one Ctrl-C terminates
    all of them. Frontend/admin are skipped with a warning when pnpm is
    unavailable or their node_modules are missing. Returns 0 after a clean
    shutdown, or 1 when every component was skipped.
    """
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["PYTHONPATH"] = SRC_PATH
    host = args.host or os.getenv("HOST", "127.0.0.1")
    port = int(args.port if args.port is not None else os.getenv("PORT", "8000"))
    reload_on = bool(args.dev) or os.getenv("MODE", "dev").lower() == "dev"

    procs = []
    if not getattr(args, "skip_backend", False):
        procs.append(_spawn_dev_server(
            "backend", BASE_DIR, SRC_PATH,
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--host", host, "--port", str(port),
             "--reload" if reload_on else "--no-reload"]))
    if not getattr(args, "skip_frontend", False):
        procs.extend(_spawn_node_app(
            "frontend", os.path.join(BASE_DIR, "src", "frontend")))
    if not getattr(args, "skip_admin", False):
        procs.extend(_spawn_node_app(
            "admin", os.path.join(BASE_DIR, "src", "admin-app")))
    if not procs:
        print("skillsynth run: nothing to start")
        return 1
    return _supervise(procs)


def _pnpm_bin():
    """Locate the pnpm executable, preferring PATH then the npm-global dir.

    Called by _spawn_node_app; returns the binary path or None when pnpm is
    genuinely unavailable, so the caller can skip that Node app with a warning
    instead of failing the whole `run` command. On Windows (os.name == "nt")
    shutil.which("pnpm") resolves pnpm.cmd and no ~/.npm-global fallback is used.
    """
    found = shutil.which("pnpm")
    if found:
        return found
    if os.name != "nt":
        alt = os.path.expanduser("~/.npm-global/bin/pnpm")
        if os.path.exists(alt):
            return alt
    return None


def _spawn_node_app(name, cwd):
    """Spawn a Node dev server under cwd if node_modules exist.

    Called by _cmd_run for the frontend and admin apps; returns a one-element
    list with the started Popen, or empty when skipped. Prefers the local
    Vite binary (node_modules/.bin/vite) so the dev server starts without
    going through pnpm's deps-status check, and falls back to `pnpm dev`
    when the Vite binary is unavailable. Runs the process in its own session
    and streams its merged output line-prefixed to the console.
    """
    if not os.path.isdir(os.path.join(cwd, "node_modules")):
        print(f"[{name}] skipped: node_modules missing — run `pnpm install` in {cwd}")
        return []
    vite_bin = os.path.join(cwd, "node_modules", ".bin", "vite")
    if os.path.exists(vite_bin):
        cmd = [vite_bin, "dev"]
    else:
        pnpm = _pnpm_bin()
        if not pnpm:
            print(f"[{name}] skipped: neither vite nor pnpm found")
            return []
        cmd = [pnpm, "dev"]
    spawn_kwargs = dict(
        cwd=cwd, env=dict(os.environ),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.name != "nt":
        spawn_kwargs["start_new_session"] = True
    else:
        spawn_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(cmd, **spawn_kwargs)
    threading.Thread(target=_pump_output, args=(name, proc), daemon=True).start()
    print(f"[{name}] started (pid {proc.pid})")
    return [proc]


def _spawn_dev_server(name, cwd, src_path, cmd):
    """Spawn the backend (uvicorn) child in its own session with prefixed logging.

    Called by _cmd_run; builds the environment (PYTHONPATH=src) and returns
    the started Popen. Session isolation lets _supervise terminate the uvicorn
    reloader and its workers together on shutdown.
    """
    spawn_kwargs = dict(
        cwd=cwd, env=dict(os.environ, PYTHONPATH=src_path),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if os.name != "nt":
        spawn_kwargs["start_new_session"] = True
    else:
        spawn_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(cmd, **spawn_kwargs)
    threading.Thread(target=_pump_output, args=(name, proc), daemon=True).start()
    print(f"[{name}] started (pid {proc.pid})")
    return proc


def _pump_output(prefix, proc):
    """Forward a child's merged stdout/stderr, line-prefixed, to the console.

    Called by _spawn_dev_server/_spawn_node_app in a daemon thread; decodes
    bytes safely and never raises, so a slow or closed stream cannot crash
    the supervisor.
    """
    try:
        for raw in iter(proc.stdout.readline, b""):
            print(f"[{prefix}] {raw.decode(errors='replace').rstrip()}", flush=True)
    except Exception:
        pass


def _supervise(procs):
    """Block on the project's child processes and terminate them on exit/signal.

    Called by _cmd_run as the supervisor; registers SIGINT/SIGTERM handlers
    (POSIX only) that SIGTERM each child's session (so uvicorn reloaders and
    Next.js children die together), then waits. Returns 0 after a clean shutdown.
    """
    def _shutdown(signum, frame):
        print("\nskillsynth run: shutting down…")
        for p in procs:
            _terminate_session(p)
        for p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                _terminate_session(p, force=True)

    if os.name != "nt":
        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)
    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        pass
    _shutdown(None, None)
    return 0


def _terminate_session(proc, force=False):
    """Terminate (or force-kill) a child's process tree so its subtree dies.

    Called by _supervise; on Windows uses taskkill /T /F on the whole tree,
    while on POSIX uses killpg on the child's session id (SIGTERM or SIGKILL),
    falling back to a direct terminate/kill when the lookup fails. SIGKILL and
    os.killpg are referenced only inside the POSIX branch.
    """
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"], check=False)
        return
    try:
        pgid = os.getpgid(proc.pid)
        os.killpg(pgid, signal.SIGKILL if force else signal.SIGTERM)
    except Exception:
        try:
            (proc.kill if force else proc.terminate)()
        except Exception:
            pass


def _cmd_seed(args):
    """Seed the SQLite file at --db by driving seed_v4's injection seam.

    Invoked by main via `skillsynth seed`; executes the real seed_v4.py with
    runpy under a non-__main__ name (its auto-run never fires), then calls its
    documented seed(engine, session_factory) seam bound to an isolated engine
    at the requested path — the dev database is never opened when --db points
    elsewhere. Returns 0, or the seed FK-gate exit code on failure.
    """
    db_path = os.path.abspath(args.db)
    namespace = runpy.run_path(
        os.path.join(BASE_DIR, "seed_v4.py"), run_name="skillsynth_cli_seed")
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
        """Apply dev-mode SQLite pragmas on every new connection.

        Registered by _make_seed_engine via event.listens_for; executes
        foreign_keys/WAL/synchronous exactly as backend.database does so
        seeded rows carry the same integrity guarantees as the running app.
        """
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


def _pnpm():
    """Resolve the pnpm executable; error string (not path) when absent."""
    return shutil.which("pnpm")


def _run(cmd, cwd):
    """Run a command in cwd, stream output to the terminal, return exit code.

    Called by the frontend/admin/verify handlers; inherits stdout/stderr so
    build and test output is visible live and the subprocess return code is
    passed straight through to the caller.
    """
    proc = subprocess.run(cmd, cwd=cwd, check=False)
    return proc.returncode


def _clean_artifacts(app_dir):
    """Remove SvelteKit/Vite build output so the next build is from scratch.

    Called by the frontend/admin build handlers (default "clean build"); drops
    .svelte-kit and build so generated client/server bundles are regenerated
    rather than incrementally reused.
    """
    for name in (".svelte-kit", "build"):
        path = os.path.join(app_dir, name)
        if os.path.isdir(path):
            shutil.rmtree(path)


def _install(app_dir):
    """pnpm install in app_dir; returns 1 with a clear message if pnpm missing."""
    pnpm = _pnpm()
    if not pnpm:
        print("ERROR: pnpm not found on PATH — install pnpm to build the apps")
        return 1
    return _run([pnpm, "install"], cwd=app_dir)


def _cmd_frontend(args):
    """pnpm check|build the student frontend with optional from-scratch deps.

    Invoked by main via `skillsynth frontend {check|build} [--clean-deps]`;
    build always cleans .svelte-kit/build first, --clean-deps also wipes
    node_modules and reinstalls. Returns the pnpm exit code.
    """
    app_dir = os.path.join(SRC_PATH, "frontend")
    pnpm = _pnpm()
    if not pnpm:
        print("ERROR: pnpm not found on PATH — install pnpm to build the apps")
        return 1
    if args.clean_deps:
        shutil.rmtree(os.path.join(app_dir, "node_modules"), ignore_errors=True)
        rc = _run([pnpm, "install"], cwd=app_dir)
        if rc:
            return rc
    if args.action == "build":
        _clean_artifacts(app_dir)
        return _run([pnpm, "build"], cwd=app_dir)
    return _run([pnpm, "check"], cwd=app_dir)


def _cmd_admin(args):
    """pnpm check|build the admin app with optional from-scratch deps.

    Invoked by main via `skillsynth admin {check|build} [--clean-deps]`;
    mirrors _cmd_frontend against src/admin-app. Returns the pnpm exit code.
    """
    app_dir = os.path.join(SRC_PATH, "admin-app")
    pnpm = _pnpm()
    if not pnpm:
        print("ERROR: pnpm not found on PATH — install pnpm to build the apps")
        return 1
    if args.clean_deps:
        shutil.rmtree(os.path.join(app_dir, "node_modules"), ignore_errors=True)
        rc = _run([pnpm, "install"], cwd=app_dir)
        if rc:
            return rc
    if args.action == "build":
        _clean_artifacts(app_dir)
        return _run([pnpm, "build"], cwd=app_dir)
    return _run([pnpm, "check"], cwd=app_dir)


def _cmd_verify(args):
    """Full from-scratch verification across both apps + backend, stop on fail.

    Invoked by main via `skillsynth verify [--clean-deps]`; runs frontend
    svelte-check, admin svelte-check, frontend build, admin build (clean
    artifacts every run; --clean-deps also reinstalls node_modules), backend
    pytest, schema verify and doctor. Prints a per-stage PASS/FAIL summary and
    returns the first non-zero stage exit code, or 0 when all stages pass.
    """
    stages = [
        ("frontend svelte-check",
         lambda: _cmd_frontend(argparse.Namespace(action="check", clean_deps=False))),
        ("admin svelte-check",
         lambda: _cmd_admin(argparse.Namespace(action="check", clean_deps=False))),
        ("frontend build",
         lambda: _cmd_frontend(argparse.Namespace(action="build", clean_deps=args.clean_deps))),
        ("admin build",
         lambda: _cmd_admin(argparse.Namespace(action="build", clean_deps=args.clean_deps))),
        ("backend pytest",
         lambda: _cmd_test(argparse.Namespace(pytest_args=[]))),
        ("schema verify", lambda: _cmd_schema(argparse.Namespace())),
        ("doctor", lambda: _cmd_doctor(argparse.Namespace(strict=False))),
    ]
    print("=== SkillSynth full verification (from-scratch build) ===")
    results = []
    failed = None
    for name, fn in stages:
        print(f"\n--- {name} ---")
        rc = fn()
        results.append((name, rc))
        if rc != 0 and failed is None:
            failed = (name, rc)
            break
    print("\n=== Verification summary ===")
    for name, rc in results:
        print(f"  [{'PASS' if rc == 0 else 'FAIL'}] {name}")
    if failed:
        print(f"\nVerification FAILED at stage '{failed[0]}' (exit {failed[1]}).")
        return failed[1]
    print("\nVerification PASSED — all stages green.")
    return 0
