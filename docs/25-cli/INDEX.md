# SS-EDS: CLI

## Purpose
Document the `skillsynth` console entrypoint and every script that actually exists: the installed `skillsynth` command (run/seed/test/schema/doctor/version), the `./skillsynth` root shim, legacy `run.py`, `seed_v3.py`, `tools/verify_schema.py`, pytest, and the pnpm task runners for both frontends.

## Responsibilities
- Provide the canonical command table with working directories
- Document seed, verification, and doctor workflows
- Point to the environment each command expects

## Inputs
- Developer workflow needs (run, seed, verify, test, doctor)
- pyproject.toml `[project.scripts]` + requirements.txt / pnpm manifests

## Outputs
- Repeatable commands for every verification gate in 16-testing

## Dependencies
- 07-backend (`backend.cli`, run.py)
- 10-database (seed_v3.py, tools/verify_schema.py)
- 08-frontend / 09-admin (pnpm scripts)

## Command Reference
| Command | Purpose | Working Dir |
|---------|---------|-------------|
| `skillsynth run [--host H] [--port P] [--dev]` | Serve FastAPI backend via uvicorn; HOST/PORT/MODE env defaults, flags override; reload when MODE=dev or --dev | repo root |
| `skillsynth seed [--db PATH]` | Seed all 15 tables (~1,109 rows, idempotent, FK-gated) into PATH (default skillsynth.db); dev DB never touched when --db points elsewhere | repo root |
| `skillsynth test [args...]` | Run `pytest tests/` in a subprocess (PYTHONPATH=src); exit code passthrough | repo root |
| `skillsynth schema` | Run tools/verify_schema.py → prints SCHEMA MATCH; exit code passthrough | repo root |
| `skillsynth doctor [--strict]` | Env health table: fastapi/sqlalchemy/uvicorn imports, AI_ENABLED, GGUF model file (+size), llama_cpp only when AI is on, skillsynth.db; always exits 0 unless --strict | repo root |
| `skillsynth version` | Print name + version (importlib.metadata → pyproject fallback) | anywhere |
| `python run.py` | Legacy launcher — thin shim delegating to `skillsynth run` (identical behavior) | repo root |
| `PYTHONPATH=src python seed_v3.py` | Direct seed of the dev database (same engine as `skillsynth seed`) | repo root |
| `PYTHONPATH=src python tools/verify_schema.py` | Direct DDL ↔ ORM verification | repo root |
| `PYTHONPATH=src python -m pytest tests/ -q` | Backend suite directly (what `test` wraps) | repo root |
| `pnpm dev` | Student frontend dev server :3000 | src/frontend |
| `pnpm build` / `pnpm type-check` / `pnpm lint` | Build / tsc --noEmit / next lint | src/frontend |
| `pnpm dev` / `pnpm build` / `pnpm type-check` | Admin app dev/build/check (:3001) | src/admin-app |
| `bash start.sh` | Full-stack launcher (venv + pnpm PATH bootstrap) | repo root |
| `docker compose up -d` | Container stack: backend/frontend/admin | repo root |

## Installation & Resolution Order
1. `.venv/bin/pip install -e .` installs the `skillsynth` script from pyproject.toml (`backend.cli:main`)
2. The root `./skillsynth` bash shim execs `.venv/bin/skillsynth` when present, else falls back to `PYTHONPATH=src python -m backend.cli`
3. `cli.main(argv=None)` returns int exit codes; the console wrapper converts them via sys.exit

## Sequence: First-Run Bootstrap
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
skillsynth seed                           # create + populate skillsynth.db
skillsynth run                            # API live on :8000
```

## Seed & Verification Scripts
| Script | Scope | Notes |
|--------|-------|-------|
| seed_v3.py (via `seed`) | All 15 tables | Single authoritative seed; rebuilds schema from ORM metadata then inserts; PRAGMA foreign_key_check gate; `--db` drives an isolated engine so parallel/dev DBs stay safe |
| tools/verify_schema.py (via `schema`) | Tables/columns/PKs/FKs/ON DELETE/uniques | Compares canonical DDL against ORM; prints SCHEMA MATCH on success |

Removed tooling (one line): legacy seed scripts, TypeScript ad-hoc test scripts, standalone admin-creation scripts, and the old `tools/cli/` package no longer exist; admin provisioning happens via ADMIN_EMAIL/ADMIN_PASSWORD at startup or admin CRUD.

## Rules
1. Python commands run from repo root; the CLI injects PYTHONPATH=src itself
2. pnpm commands run from `src/frontend` or `src/admin-app` — never npm
3. seed_v3.py is idempotent; re-running it is always safe in dev; use `--db` to target any other file without touching the dev database
4. Tests use their own temp DB — never point pytest at skillsynth.db
5. doctor is a diagnostic only: non-strict runs always exit 0; treat WARN rows as informational

## Examples
```bash
# Typical verification loop before a merge:
skillsynth test -q                        # or: skillsynth test --maxfail=1 -x
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
skillsynth schema                         # SCHEMA MATCH expected
skillsynth doctor --strict                # all required checks OK

# Isolated seed for experiments:
skillsynth seed --db /tmp/opencode/experiment.db
```

## Edge Cases
- pnpm missing from PATH → `export PATH="$HOME/.npm-global/bin:$PATH"` (start.sh does this automatically)
- Port already bound (8000/3000/3001) → stop the process or pass `run --port P`
- `skillsynth test -k auth` style dashed args work (main short-circuits `test` before argparse)
- Uninstalled package → `./skillsynth` shim still works through the `python -m backend.cli` fallback

## Failure Cases
- seed fails on FK violation → fix ordering/data in seed_v3.py; it refuses partial states by design (exit code propagates through the CLI)
- verify_schema mismatch → DDL and ORM drifted; align both before merging (exit 1)

## Recovery Procedures
1. Delete skillsynth.db and re-run `skillsynth seed` for a clean dev database
2. Reinstall deps (`pip install -r requirements.txt && pip install -e .` / `pnpm install`) after manifest changes

## Refactoring Strategy
- Any new subcommand must be added to this table or deleted outright — no undocumented scripts
