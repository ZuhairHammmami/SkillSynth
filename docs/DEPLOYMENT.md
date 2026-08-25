# Build & Deployment

## Build Commands

```bash
# Frontend (runs tsc --noEmit then next build)
cd src/frontend && pnpm build

# Backend (no explicit build step)
# Just ensure requirements installed:
pip install -r requirements.txt
```

## Run Commands

```bash
# Development
python run.py                              # Backend :8000 (auto-reload in dev mode)
cd src/frontend && pnpm dev                # Frontend :3000
bash start.sh                              # Full stack (but uses npm instead of pnpm)

# Production
python run.py                              # MODE=prod (no --reload)
cd src/frontend && pnpm start              # Production server
```

## Environment Variables

### Root `.env` — Backend

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `MODE` | Yes | `dev` | `dev`=SQLite, `prod`=PostgreSQL |
| `SECRET_KEY` | Prod only | dev fallback | JWT signing key |
| `DATABASE_URL` | Prod | — | PostgreSQL (Supabase) connection |
| `ADMIN_EMAIL` | No | `admin@skillsynth.io` | Auto-created admin |
| `ADMIN_PASSWORD` | For admin | — | Auto-create admin if set |
| `SENDGRID_API_KEY` | For email | — | Password reset emails |
| `LLM_PROVIDER` | No | `hybrid` | `local`, `openai`, or `hybrid` |
| `OPENAI_API_KEY` | For OpenAI | — | Required for OpenAI provider |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Local LLM endpoint |

### `src/frontend/.env.local` — Frontend

| Variable | Example | Notes |
|----------|---------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://127.0.0.1:8000` | FastAPI backend URL |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://*.supabase.co` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJ...` | Supabase anon key |

## Deployment — DEPRECATED (absorbed into SS-EDS docs/17-deployment/)

> **⚠️ `CLI tool` row — CLI tool removed.** Targets

### Render (Backend)
- Root dir: `backend`
- Build: `pip install -r requirements.txt`
- Start: `python main.py`

### Vercel (Frontend)
- CORS origins include `https://skillsynth.vercel.app`
- Framework preset: Next.js

## Supabase

- **Project URL**: `https://pvhykpqjwftqqmzxaynx.supabase.co`
- **Project ref**: `pvhykpqjwftqqmzxaynx`
- **Migrations**: 5 SQL files in `src/migrations/` — **apply manually via Supabase SQL editor**
- **Client**: `src/frontend/src/lib/supabase.ts` (browser client, not used in auth flow)
- **Types**: `src/frontend/src/types/supabase.ts` (4 tables only)

## Package Manager Notes

| Area | Correct | start.sh uses | CI uses |
|------|---------|---------------|---------|
| Frontend | **pnpm** | `npm` (incorrect) | `npm` (incorrect) |
| CLI tool | **npm** | n/a | n/a |
| Python | **pip** | `pip` | `pip` |

## File Watching / Reload

- Backend: `--reload` auto-enabled when `MODE=dev`
- Frontend: `next dev` (HMR)
