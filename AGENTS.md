# SkillSynth — Agent Guide

## Architecture (Two Backends)

- **FastAPI (primary backend)**: `src/backend/` — Python, port 8000. Run via `python run.py`. Imports use `from backend import X` (path is `src/`, injected by `run.py`).
- **Next.js API routes**: `src/frontend/src/app/api/` — thin wrappers for LLM calls and search. Not a replacement for FastAPI.
- **Frontend**: `src/frontend/` — Next.js 14 + React 18. **pnpm** (not npm). Package mismatches between root `package.json` and `src/frontend/package.json` — work in `src/frontend/`.

## Database

- `MODE=dev` (default) → SQLite at `skillsynth.db` (repo root).
- `MODE=prod` → PostgreSQL via `DATABASE_URL` env var (Supabase).
- SQLAlchemy auto-creates tables on startup (`main.py` startup event).
- Supabase migrations are `.sql` files in `src/migrations/` — apply via Supabase SQL editor, not code.

## Developer Commands

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py                              # dev: --reload auto-enabled when MODE=dev

# Frontend
cd src/frontend && pnpm install && pnpm dev   # :3000

# Verification
python verify-db-setup.py                    # checks DB mode + tables
bash verify-aeis-setup.sh                    # checks AEIS schema files
bash verify-phase2-neural-operation.sh       # checks Phase 2 components

# Type-checking
cd src/frontend && pnpm type-check           # tsc --noEmit

# Linting
cd src/frontend && pnpm lint                 # next lint

# Admin user creation
python src/backend/create_admin.py

# Seed Supabase concepts table
node seed-database.js                        # reads .env manually (no dotenv)
```

## Key Quirks

- **Imports in backend** assume `src/` is on `PYTHONPATH` — use `from backend import models`, not `from src.backend import models`.
- **API client** in frontend (`src/frontend/src/shared/lib/api.ts`) uses Axios; the target is `http://127.0.0.1:8000` (from `NEXT_PUBLIC_API_BASE_URL`).
- **Auth middleware** checks `authToken` cookie (not Supabase session). Routes protected: `/dashboard`, `/wizard`, `/paths`. Auth routes: `/login`, `/register`.
- **Frontend is RTL/Arabic-first**: `layout.tsx` sets `<html lang="ar" dir="rtl">` with Tajawal font. No LTR toggle exists.
- **HybridLLMProvider** (`src/services/HybridLLMProvider.ts`) is **outside** the frontend src directory — it's its own module under `src/services/`. Import as `@/services/...` via tsconfig paths (aliased to `src/frontend/src/*` only — verify resolution works).
- **LLM requires Ollama** running at `localhost:11434` for local mode. Without it, `LLM_PROVIDER=hybrid` falls back to OpenAI (needs `OPENAI_API_KEY`).
- **No test framework** is configured. `run_test.py` is a manual integration test (Python backend), no Jest/Vitest config exists.
- **Supabase integration is partial**: `@supabase/ssr` installed, `supabase.ts` client exists, but most API routes still have `TODO` comments and use mock data.
- **Conventional commits** expected per `CONTRIBUTING.md`: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`.

## Environment Files

- Root `.env` — backend config (DB, LLM, API keys). **Contains live credentials**.
- `src/frontend/.env.local` — frontend vars (`NEXT_PUBLIC_*`). **Also contains live Supabase keys**.
- `seed-database.js` parses `.env` manually (regex — not `dotenv`).

## Build & Deploy

- Frontend build: `cd src/frontend && pnpm build` (runs `tsc --noEmit && next build`).
- Backend deploy (Render): root dir = `backend`, build = `pip install -r requirements.txt`, start = `python main.py`.
- No CI/CD workflows found in `.github/`.
