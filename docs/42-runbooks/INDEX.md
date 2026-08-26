# SS-EDS: Runbooks

## Purpose
Copy-paste operational procedures for SkillSynth using only commands that exist in this repository. Every command below was verified against the current tree.

## Responsibilities
- Provide boot, seed, verify, and reset runbooks
- Document admin recovery and failure triage

## Inputs
- Repository root layout (run.py, seed_v3.py, tools/, src/)
- .env / src/frontend/.env.local configuration

## Outputs
- Working environments (:8000 backend, :3000 student app, :3001 admin app)
- Green verification pipeline

## Dependencies
- 17-deployment (container builds, env vars)
- 34-error-handling (failure semantics referenced by triage)

## Runbook: Fresh Development Setup
```bash
# 1. Backend (repo root)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                # edit values as needed

# 2. Database — creates schema + ~1100 rows (15 tables, FK-gated, idempotent)
PYTHONPATH=src python seed_v3.py

# 3. Student frontend
cd src/frontend && pnpm install     # pnpm is required, not npm
# .env.local needs NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# 4. Admin app (second Next.js process)
cd src/admin-app && pnpm install    # same NEXT_PUBLIC_API_BASE_URL variable

# 5. Start (three terminals)
source .venv/bin/activate && python run.py        # :8000
cd src/frontend && pnpm dev                       # :3000
cd src/admin-app  && pnpm dev                     # :3001
```

## Runbook: Full Verification Pipeline
```bash
PYTHONPATH=src python -m pytest tests/ -q            # 199 tests, isolated temp DB
PYTHONPATH=src python tools/verify_schema.py         # → SCHEMA MATCH
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
```

## Runbook: Database Reset
```bash
rm skillsynth.db
PYTHONPATH=src python seed_v3.py                     # recreate + reseed
sqlite3 skillsynth.db "PRAGMA foreign_key_check;"    # → no rows (clean)
```

## Runbook: Admin Account Recovery
```bash
# Preferred: startup auto-creation (idempotent)
export ADMIN_EMAIL=admin@skillsynth.io
export ADMIN_PASSWORD='NewAdmin@123456'
python run.py                                        # created/upgraded at boot

# Seeded accounts (passwords in AGENTS.md): admin@skillsynth.io, demo@demo.com,
# editor@skillsynth.io, veteran@skillsynth.io, student2@skillsynth.io
```

## Runbook: Backend Won't Start
```bash
python run.py 2>&1 | tail -20
# MODE=prod without DATABASE_URL → startup refuses; set it or use dev MODE
# Port 8000 busy → fuser -k 8000/tcp (dev machine only)
# Import errors → confirm you ran from repo root so run.py injects src/
```

## Runbook: Data Triage
```bash
sqlite3 skillsynth.db "SELECT count(*) FROM paths;"
sqlite3 skillsynth.db "SELECT * FROM activity_log ORDER BY id DESC LIMIT 10;"
curl -s localhost:8000/api/public/stats              # 30s-cached public counters
```

## Rules
1. Only commands that exist here are documented — no migration-framework CLI, no legacy seed scripts, no make targets
2. Tests never touch skillsynth.db (conftest builds a temp DB per run)
3. Every destructive step names its blast radius before running
4. Runbooks are re-verified after any change to run.py, seed_v3.py, or tools/

## Examples
- "Schema drift suspected" → run tools/verify_schema.py; SCHEMA MATCH clears the suspicion

## Edge Cases
- pnpm missing from PATH → export PATH="$PATH:$HOME/.npm-global/bin"
- Seed interrupted mid-run → rerun; seed_v3 is drop/recreate + idempotent inserts

## Failure Cases
- verify_schema reports mismatch → DDL and ORM diverged; fix entities or DDL before anything else
- pytest failures after pulling → recreate venv, reinstall requirements.txt

## Recovery Procedures
1. Worst case DB state → delete file + reseed (no persistent state lives outside skillsynth.db)
2. Frontend cache weirdness → rm -rf .next && pnpm dev

## Refactoring Strategy
- Convert repeated triage into tools/ scripts instead of growing this page
