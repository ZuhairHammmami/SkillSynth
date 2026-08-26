# SkillSynth

SkillSynth is an **adaptive learning platform**: a FastAPI + Next.js system that builds personalized, skill-based learning paths from a prerequisite DAG — with assessments, gap analysis, analytics, SSE real-time updates, and a separate admin console with full CRUD and referential-integrity guards. Arabic-first (RTL) UI for learners. Documentation follows the SS-EDS system in [`docs/INDEX.md`](docs/INDEX.md).

**Stack**: FastAPI + SQLAlchemy (Clean Architecture) · Next.js 14 + React 18 + Tailwind (pnpm) · SQLite (dev) / PostgreSQL (prod), strict-3NF 15 tables.

## Project Structure

```
src/backend/     FastAPI API — routers/ services/ repositories/ entities/ dto/
                 policies/ middlewares/ events/ + database.py, main.py, config/
src/frontend/    Student app :3000 — src/{app,shared,i18n,types} + middleware.ts,
                 bilingual ar/en, RTL-first
src/admin-app/   Admin app :3001 — English-only, CRUD dialogs + force-delete flow
docs/            SS-EDS documentation (50 numbered sections, each with INDEX.md)
seed_v3.py       15-table seed (~1109 rows, FK-gated, idempotent)
tools/           verify_schema.py and other repo tooling
tests/           pytest suite (143 tests, isolated temp DB per run)
```

## Quick Start

```bash
# Backend (:8000) — OpenAPI UI at /docs
source .venv/bin/activate && pip install -r requirements.txt && PYTHONPATH=src python run.py

# Student frontend (:3000)
cd src/frontend && pnpm dev

# Admin app (:3001)
cd src/admin-app && pnpm dev

# Seed database (idempotent; safe to re-run)
PYTHONPATH=src python seed_v3.py
```

## Installation

```bash
# Base install (FastAPI backend + CLI)
pip install -r requirements.txt && pip install -e .

# Optional SS-AI local inference (CUDA build optional)
pip install -r requirements-ai.txt
```

**Model note:** place the `Llama-3.2-3B-Instruct-Q6_K.gguf` GGUF (~2.46 GiB, gitignored, user-supplied) into `src/data/`; `skillsynth doctor --strict` verifies its presence when `AI_ENABLED=true`. `AI_ENABLED` defaults to `false`.

## Tests & Verification

```bash
PYTHONPATH=src python -m pytest tests/ -q        # 143 passed; isolated temp DB, dev DB untouched
PYTHONPATH=src python tools/verify_schema.py     # prints SCHEMA MATCH on success
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
```

## API Surface

7 routers (`auth`, `learning`, `paths`, `assessments`, `analytics`, `admin`, `realtime`) exposing **63 operations across 49 paths**. Writes are integrity-guarded: unknown references and cycles → 400, rename collisions → 409, restricted deletes → 409 census unless `?force=true` (see [ADR-014](docs/41-decision-records/adr-014.md)).

Seed credentials and repo conventions live in [AGENTS.md](AGENTS.md). See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.
