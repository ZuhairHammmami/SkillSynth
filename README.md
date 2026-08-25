# SkillSynth

SkillSynth is an **Adaptive Learning OS**: a FastAPI + Next.js platform that builds personalized, skill-based learning paths from a prerequisite graph, with assessments, analytics, real-time updates, and a separate admin console. Arabic-first (RTL) UI for learners; documentation follows the SS-EDS system in [`docs/`](docs/INDEX.md).

## Architecture

| Component | Tech | Location | Port |
|-----------|------|----------|------|
| Backend API | FastAPI + SQLAlchemy (Clean Architecture) | `src/backend/` | 8000 |
| Student frontend | Next.js 14 + React 18 + Tailwind (bilingual ar/en) | `src/frontend/` | 3000 |
| Admin app | Separate Next.js app (English-only) | `src/admin-app/` | 3001 |
| Database | SQLite (dev) / PostgreSQL (prod), 15 domain tables, strict 3NF | `skillsynth.db`, DDL in `src/migrations/003_reduced_schema.sql` | — |

## Quick Start

**Backend (port 8000)**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python seed_v3.py    # seed 1109 rows into all 15 tables (FK-gated, idempotent)
python run.py                       # http://localhost:8000 (docs at /docs)
```

**Student frontend (port 3000)**
```bash
export PATH="$PATH:/home/zuhair/.npm-global/bin"   # if pnpm is not on PATH
cd src/frontend && pnpm install && pnpm dev        # http://localhost:3000
```

**Admin app (port 3001)**
```bash
cd src/admin-app && pnpm install && pnpm dev       # http://localhost:3001
```

**Tests**
```bash
PYTHONPATH=src python -m pytest tests/ -q           # 79 tests against an isolated temp DB
```

## Verification

```bash
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
PYTHONPATH=src python -m pytest tests/ -q
PYTHONPATH=src python tools/verify_schema.py       # prints SCHEMA MATCH on success
```

Seed credentials and repo conventions live in [AGENTS.md](AGENTS.md). See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.