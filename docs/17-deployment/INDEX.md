# SS-EDS: Deployment

> **Source**: Migrated from docs/DEPLOYMENT.md

## Purpose
Document build, deployment, environment configuration, and infrastructure for SkillSynth. Covers development and production modes, target platforms (Render, Vercel, Supabase), and environment variables.

## Responsibilities
- Define build and deployment commands
- Manage environment variable configuration (.env, .env.local)
- Document deployment targets (Render, Vercel, Supabase)
- Handle database migration strategy
- Maintain start.sh and run.py entrypoints

## Inputs
- Infrastructure requirements
- Environment variable specifications
- Deployment platform documentation

## Outputs
- Build commands
- Deployment configurations
- Environment templates

## Dependencies
- 07-backend (Python deployment)
- 08-frontend (Next.js deployment)
- 10-database (migration scripts)
- 14-security (production secrets management)

## Sequence: Full Stack Deployment
```
Code Push → Render Deploy (Backend) → Vercel Deploy (Frontend) → Supabase Migrate (DB) → Health Check
```

## Build Commands
```bash
# Frontend (runs tsc --noEmit then next build)
cd src/frontend && pnpm build

# Backend (ensure requirements installed)
pip install -r requirements.txt

# Development
python run.py                        # Backend :8000 (auto-reload in dev)
cd src/frontend && pnpm dev          # Frontend :3000
bash start.sh                        # Full stack (but uses npm instead of pnpm)

# Production
python run.py                        # MODE=prod (no --reload)
cd src/frontend && pnpm start        # Production server
```

## Environment Variables
| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| MODE | Yes | dev | dev=SQLite, prod=PostgreSQL |
| SECRET_KEY | Prod | Dev fallback | JWT signing |
| DATABASE_URL | Prod | — | PostgreSQL (Supabase) |
| SENDGRID_API_KEY | Email | — | Password reset |
| LLM_PROVIDER | No | hybrid | local/openai/hybrid |
| OPENAI_API_KEY | OpenAI | — | OpenAI LLM |

## ERD References
- No deployment-specific tables
- Database migrations in src/migrations/*.sql

## Rules
1. Frontend uses pnpm, not npm
2. start.sh incorrectly uses npm — use pnpm directly
3. CORS origins include https://skillsynth.vercel.app for production
4. Supabase migrations must be applied manually via SQL editor
5. Run backend from repo root via `python run.py` (run.py adds src/ to path)

## Examples
- Render: Root dir `backend`, Build `pip install -r requirements.txt`, Start `python main.py`
- Vercel: Framework preset Next.js, CORS configured for skillsynth.vercel.app

## Edge Cases
- MODE=prod without DATABASE_URL → startup error
- Frontend cannot reach backend at NEXT_PUBLIC_API_BASE_URL
- package.json in repo root conflicts with frontend's package.json

## Failure Cases
- Build fails due to incorrect working directory
- Package manager mismatch (npm vs pnpm)
- Missing environment variables in production

## Recovery Procedures
1. Verify MODE and DATABASE_URL environment variables
2. Check frontend can reach backend API
3. Confirm CORS origins include deployment domain

## Refactoring Strategy
- Add Docker Compose for consistent local development
- Move from manual Supabase migrations to automated CI/CD
- Fix start.sh to use pnpm instead of npm
- Add health check endpoints for deployment monitoring
