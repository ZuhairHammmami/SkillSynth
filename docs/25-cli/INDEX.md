# SS-EDS: CLI

## Purpose
Document the command-line entry points and scripts that actually exist: `run.py` (backend), `seed_v3.py` (seed), `tools/verify_schema.py` (schema verifier), pytest, and the pnpm task runners for both frontends.

## Responsibilities
- Provide the canonical command table with working directories
- Document seed and verification workflows
- Point to the environment each command expects

## Inputs
- Developer workflow needs (run, seed, verify, test, build)
- requirements.txt / pnpm manifests

## Outputs
- Repeatable commands for every verification gate in 16-testing

## Dependencies
- 07-backend (run.py)
- 10-database (seed_v3.py, tools/verify_schema.py)
- 08-frontend / 09-admin (pnpm scripts)

## Command Reference
| Command | Purpose | Working Dir |
|---------|---------|-------------|
| `python run.py` | Start FastAPI backend on :8000 (uvicorn; reload when MODE=dev) | repo root |
| `PYTHONPATH=src python seed_v3.py` | Seed all 15 tables (~1,100 rows, idempotent, FK-gated) | repo root |
| `PYTHONPATH=src python tools/verify_schema.py` | Verify DDL ↔ ORM parity → prints SCHEMA MATCH | repo root |
| `PYTHONPATH=src python -m pytest tests/ -q` | Run the 178-test backend suite (isolated temp DB) | repo root |
| `pnpm dev` | Student frontend dev server :3000 | src/frontend |
| `pnpm build` / `pnpm type-check` / `pnpm lint` | Build / tsc --noEmit / next lint | src/frontend |
| `pnpm dev` / `pnpm build` / `pnpm type-check` | Admin app dev/build/check (:3001) | src/admin-app |
| `bash start.sh` | Full-stack launcher (venv + pnpm PATH bootstrap) | repo root |
| `docker compose up -d` | Container stack: backend/frontend/admin | repo root |

## Sequence: First-Run Bootstrap
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python seed_v3.py          # create + populate skillsynth.db
python run.py                             # API live on :8000
```

## Seed & Verification Scripts
| Script | Scope | Notes |
|--------|-------|-------|
| seed_v3.py | All 15 tables | Single authoritative seed; rebuilds schema from ORM metadata then inserts; PRAGMA foreign_key_check gate |
| tools/verify_schema.py | Tables/columns/PKs/FKs/ON DELETE/uniques | Compares canonical DDL against ORM; prints SCHEMA MATCH on success |

Removed tooling (one line): legacy seed scripts, TypeScript ad-hoc test scripts, standalone admin-creation scripts, and the old `tools/cli/` package no longer exist; admin provisioning happens via ADMIN_EMAIL/ADMIN_PASSWORD at startup or admin CRUD.

## Rules
1. Python commands run from repo root with `PYTHONPATH=src`
2. pnpm commands run from `src/frontend` or `src/admin-app` — never npm
3. seed_v3.py is idempotent; re-running it is always safe in dev
4. Tests use their own temp DB — never point pytest at skillsynth.db

## Examples
```bash
# Typical verification loop before a merge:
PYTHONPATH=src python -m pytest tests/ -q
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
PYTHONPATH=src python tools/verify_schema.py
```

## Edge Cases
- pnpm missing from PATH → `export PATH="$HOME/.npm-global/bin:$PATH"` (start.sh does this automatically)
- Port already bound (8000/3000/3001) → stop the process or override PORT

## Failure Cases
- seed fails on FK violation → fix ordering/data in seed_v3.py; it refuses partial states by design
- verify_schema mismatch → DDL and ORM drifted; align both before merging

## Recovery Procedures
1. Delete skillsynth.db and re-run seed_v3.py for a clean dev database
2. Reinstall deps (`pip install -r requirements.txt` / `pnpm install`) after manifest changes

## Refactoring Strategy
- Any new script must be added to this table or deleted outright — no undocumented scripts
