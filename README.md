# SkillSynth

> An **adaptive learning OS**: a FastAPI + SvelteKit platform that builds personalized,
> skill-based learning paths from a prerequisite DAG — with assessments, gap analysis,
> analytics, SSE real-time updates, and a separate admin console. Arabic-first (RTL)
> learner UI. Docs follow the SS-EDS system in [`docs/INDEX.md`](docs/INDEX.md).

**Stack**: FastAPI + SQLAlchemy (Clean Architecture) · SvelteKit + Svelte 5 + TypeScript
(adapter-node, pnpm) · SQLite (dev) / PostgreSQL (prod), strict-3NF across 15 tables.

---

## 1. Features

- **Adaptive path builder** — deterministic prerequisite topological sort; wizard
  scoring for full paths or per-skill generation; duplicate/mastered guards (409).
- **Assessments & placement** — questions per skill and per role, with results written
  back to `user_skills`; leveled per-skill testing including a placement test.
- **Gap analysis & analytics** — mastered skills, learning velocity, skill growth,
  path progress, learning history.
- **Real-time** — SSE event streams for learning progress and AI feedback.
- **Learner catalog** — browse categories → skills → detail with prerequisite and
  recommended strips; generate a path for any skill in one click.
- **Admin console** — full CRUD (users, skills, categories, resources, job roles) with
  referential-integrity guards, feature flags, backups, and system health.
- **SS-AI (optional)** — local LLM inference for quizzes, tests, and explanations
  (off by default; see §10).
- **Bilingual AR/EN** — 100% localized, RTL-first learner experience.

## 2. Architecture

```
┌──────────────┐   ┌──────────────────┐   ┌───────────────────┐
│ Frontend     │   │ Admin App        │   │ Backend (FastAPI) │
│ SvelteKit    │   │ SvelteKit        │   │  :8000 /docs      │
│  :3000       │   │  :3001           │   └─────────┬─────────┘
└──────┬───────┘   └────────┬─────────┘             │
       └────────────────────┼───────────────────────┘
                 REST + SSE (JWT Bearer)
                             │
                   ┌─────────▼─────────┐
                   │ SQLite (dev)      │
                   │ PostgreSQL (prod) │  15 tables, strict 3NF
                   └───────────────────┘
```

- **Backend** — `src/backend/` 8 layers: `routers/ services/ repositories/ entities/
  dto/ policies/ middlewares/ events/`, 88 operations across 69 paths (8 routers).
- **Frontend (student)** — `src/frontend/` :3000, bilingual ar/en, RTL-first.
- **Admin** — `src/admin-app/` :3001, English-only, full CRUD + force-delete flow.

Canonical DDL lives at `src/migrations/003_reduced_schema.sql`; `tools/verify_schema.py`
compares it against the ORM and prints `SCHEMA MATCH`.

## 3. Prerequisites

- **Python 3.12+** (recommended) with `venv` support.
- **Node.js 18+** and **pnpm** (for the frontend apps).
- **Git** for cloning.

| Tool | Linux | macOS | Windows (PowerShell) |
|------|-------|-------|----------------------|
| Python | `python3` | `python3` / Homebrew | `python` (Python.org) |
| pnpm | `npm i -g pnpm` | `npm i -g pnpm` | `npm i -g pnpm` |

## 4. Installation

```bash
git clone <your-repo-url> && cd SkillSynth
python -m venv .venv
source .venv/bin/activate        # Linux/macOS — Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .                 # installs the `skillsynth` CLI
```

Install frontend dependencies:

```bash
cd src/frontend && pnpm install && cd ../..
cd src/admin-app && pnpm install && cd ../..
```

Cross-platform note: all steps are OS-agnostic apart from activating the venv
(`.venv\Scripts\activate` on Windows) and the Python executable name (`python` on
Windows, `python3` optional on Linux/macOS).

## 5. Developer Quick Start

SQLite (dev) mode is zero-config — no database server required.

```bash
# Option A — one command for the full stack (backend :8000 + frontend :3000 + admin :3001)
skillsynth run

# Option B — run each service separately
source .venv/bin/activate
PYTHONPATH=src python run.py          # backend :8000, OpenAPI at /docs
cd src/frontend && pnpm dev           # student app :3000
cd src/admin-app && pnpm dev          # admin app :3001
```

Seed the database (idempotent; safe to re-run):

```bash
PYTHONPATH=src python seed_v4.py      # 15-table seed, FK-gated
# or via the CLI:
skillsynth seed
```

The `skillsynth` shim (repo root) lets you run the CLI without installing:
`./skillsynth run | seed | test | schema | doctor`.

## 6. Configuration (Environment)

Copy `.env.example` to `.env` for backend settings:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

Defaults require **nothing** — the app runs on SQLite in `dev` mode. Notable variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODE` | `dev` | `dev` = SQLite, `prod` = PostgreSQL |
| `DB_PATH` | `./skillsynth.db` | SQLite file location (dev) |
| `DATABASE_URL` | empty | Postgres URL (prod only) |
| `SECRET_KEY` | `change-me` | JWT secret — set a random value in prod |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | admin@skillsynth.io | auto-created admin on startup |
| `AI_ENABLED` | `false` | toggle SS-AI local inference |

Frontend apps read `PUBLIC_API_BASE_URL`, defaulting to `http://127.0.0.1:8000/api`.
Optionally create `src/frontend/.env.local` and `src/admin-app/.env.local`.

## 7. Seed Credentials

| User | Email | Password |
|------|-------|----------|
| Admin | admin@skillsynth.io | `Admin@123456` |
| Demo | demo@demo.com | `demo123` |
| Editor | editor@skillsynth.io | `Editor@123456` |
| Veteran | veteran@skillsynth.io | `Veteran@123456` |
| Student2 | student2@skillsynth.io | `Student@123456` |

## 8. Running Tests

```bash
source .venv/bin/activate
PYTHONPATH=src python -m pytest tests/ -q        # 305 tests, isolated temp DB, dev DB untouched
PYTHONPATH=src python tools/verify_schema.py      # prints SCHEMA MATCH on success
```

Frontend checks:

```bash
cd src/frontend && pnpm check && pnpm build
cd src/admin-app && pnpm check && pnpm build
```

## 9. API Surface

**88 OpenAPI operations across 69 paths** (8 routers):

| Area | Endpoints |
|------|-----------|
| Admin | users/skills/categories/resources/job-roles CRUD, assessments, events, reports, system-health, backups, feature flags (37 ops / 21 paths) |
| Learning Engine | path generation, graph, gaps (7 ops / 7 paths) |
| AI + wizard | two-phase wizard analysis, AI quiz/test/explain (6 ops / 6 paths) |
| Analytics | dashboard, skill-growth, path-progress, learning-history (5 ops / 5 paths) |
| Catalog browse | skill detail, roles (5 ops / 5 paths) |
| Paths & Progress | path CRUD, step complete/undo (8 ops / 6 paths) |
| Auth | register, token, me, change-password, forgot/reset, sse-token, csrf (9 ops / 8 paths) |
| Assessments | per-skill and per-role questions, submit (4 ops / 4 paths) |
| Real-time | SSE event streams (4 ops / 4 paths) |

Writes are integrity-guarded (ADR-014): unknown references / cycles → 400, rename
collisions → 409, restricted deletes → 409 census unless `?force=true`.

## 10. Optional: SS-AI Local Inference

Local LLM support is **off by default** (`AI_ENABLED=false`). To enable:

```bash
# CPU build (or add -DGGML_CUDA=on with a CUDA toolkit for GPU)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
pip install -r requirements-ai.txt
```

Place `Llama-3.2-3B-Instruct-Q6_K.gguf` (~2.46 GiB, gitignored, user-supplied) into
`src/data/`, set `AI_ENABLED=true`, and verify with:

```bash
skillsynth doctor --strict
```

Bounded autonomy (ADR-015): AI proficiency ratings adjust −1/0/+1 only at
`confidence==high`, clamped 0–5, audited; deterministic scoring is never overwritten.

## 11. Project Structure

```
src/backend/     FastAPI — routers/ services/ repositories/ entities/ dto/
                 policies/ middlewares/ events/ + database.py, main.py
src/frontend/    Student app :3000 — src/{lib,routes}, AR/EN, RTL-first
src/admin-app/   Admin app :3001 — English-only
src/migrations/  canonical DDL (003_reduced_schema.sql)
seed_v4.py       15-table deterministic seed (~1109 rows, FK-gated, idempotent)
tools/           verify_schema.py + repo tooling
tests/           pytest suite (305 tests, isolated temp DB)
docs/            SS-EDS documentation (50+ numbered sections, each with INDEX.md)
docker-compose.yml / Dockerfile(s)   containerized full stack
```

## 12. Docker (Containerized)

```bash
cp .env.example .env         # defaults to SQLite dev stack
docker compose up -d --build
# backend :8000 · frontend :3000 · admin :3001
```

The backend persists SQLite via a named volume (`skillsynth-data` → `/app/data`,
`DB_PATH=/app/data/skillsynth.db`) so WAL files survive restarts. For PostgreSQL
production, set `MODE=prod` and `DATABASE_URL` in `.env`. Frontend and admin images
build with SvelteKit adapter-node.

## 13. Documentation

- **SS-EDS**: `docs/INDEX.md` (master table of contents) — 50+ section dirs with `INDEX.md`.
- **Backend**: `docs/07-backend/` · **Frontend**: `docs/08-frontend/` · **Database**: `docs/10-database/` + `docs/40-diagrams/ERD.md`.
- **Decision records**: schema reduction (`adr-013`), referential integrity (`adr-014`),
  local LLM integration (`adr-015`).

## 14. Contributing

Repo conventions (imports, function style, file-size limits, testing, environment
files) are documented in [AGENTS.md](AGENTS.md). See [CONTRIBUTING.md](CONTRIBUTING.md)
before opening a pull request.

## 15. License & Status

- **Status**: v1.0.0 release-ready; 305 backend tests passing; `verify_schema` reports
  `SCHEMA MATCH`.
- **Security**: OWASP Top 10 practices — rate limiting, CSRF, CSP, HSTS, JWT 24h,
  account lockout, `activity_log` audit trail.
- See [CHANGELOG.md](CHANGELOG.md) for the full release history.

---

*SkillSynth — Adaptive Learning OS. Arabic-first, security-minded, SS-EDS documented.*
