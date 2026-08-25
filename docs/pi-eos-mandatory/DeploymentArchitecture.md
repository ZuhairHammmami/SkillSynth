# Deployment Architecture

## Infrastructure
| Component | Provider | Config |
|-----------|----------|--------|
| Backend API | Render (Web Service) | gunicorn + uvicorn workers, :8000 |
| Frontend | Vercel | Next.js SSR/ISR, :3000 |
| Database (prod) | Supabase | PostgreSQL, pool_size=10 |
| Database (dev) | Local | SQLite, `skillsynth.db` |
| LLM (optional) | OpenAI / Ollama | Via langchain |

## Deployment Pipeline
```
git push → GitHub
  → Render auto-deploy (backend)
  → Vercel auto-deploy (frontend)
  → Supabase migrations (manual)
```

## Environment Variables
| Variable | Source | Scope |
|----------|--------|-------|
| `MODE` | `.env` | dev/prod |
| `DATABASE_URL` | `.env` | Prod PostgreSQL URL |
| `SECRET_KEY` | `.env` | JWT signing |
| `ADMIN_EMAIL` | `.env` | Auto-create admin |
| `ADMIN_PASSWORD` | `.env` | Auto-create admin |
| `CORS_ORIGINS` | `.env` | Allowed origins |
| `NEXT_PUBLIC_API_BASE_URL` | `.env.local` | Frontend API URL |

## Start Commands
```bash
# Backend
python run.py  # uvicorn backend.main:app --reload --port 8000

# Frontend
cd src/frontend && pnpm dev  # Next.js :3000

# Seed
python seed_v2.py
```
