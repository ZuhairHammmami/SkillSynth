# SS-EDS: Deployment

## Purpose
Document how SkillSynth is built, configured, and run: `run.py`/uvicorn backend, two Next.js frontends, Docker artifacts (Dockerfile + docker-compose.yml), the start.sh launcher, and the environment variables the code actually reads.

## Responsibilities
- Define build and run commands for all three apps
- Manage configuration via .env (backend) and NEXT_PUBLIC_* vars (frontends)
- Maintain Docker images and Compose topology
- Keep schema/seed bootstrap steps documented

## Inputs
- Environment files (.env, src/frontend/.env.local)
- requirements.txt / pnpm lockfiles

## Outputs
- Backend on :8000, student frontend on :3000, admin app on :3001
- docker compose services: skillsynth-backend/-frontend/-admin

## Dependencies
- 07-backend (run.py entrypoint)
- 08-frontend / 09-admin (Next.js apps)
- 10-database (DDL + seed bootstrap)

## Sequence: Local Full Stack
```
pip install -e .                        # one-time: installs the skillsynth script
skillsynth run                          # full stack: backend :8000 + frontend :3000 + admin :3001 (reload when MODE=dev)
cd src/frontend && pnpm dev             # student frontend :3000
cd src/admin-app && pnpm dev            # admin app :3001
```
The root `./skillsynth` bash shim resolves the repo dir and execs `.venv/bin/skillsynth`, falling back to `PYTHONPATH=src python -m backend.cli` when the package is not installed — this fallback avoids only the `pip install -e .` step; backend dependencies (`pip install -r requirements.txt`) are still required on either path, so a bare checkout with no venv will not run. Legacy `python run.py` remains as a thin shim over the same code path.

## Sequence: Container Stack
```
docker compose up -d     # builds Dockerfile (python:3.14-slim multi-stage) +
                         # starts backend:8000, frontend:3000, admin:3001
docker compose down      # stop; named volumes persist data
```

## Build Commands
```bash
pip install -r requirements.txt                 # backend deps (venv recommended)
pip install -e .                                # installs the `skillsynth` console script
cd src/frontend && pnpm build                   # tsc --noEmit + next build
cd src/admin-app && pnpm build                  # same for admin
bash start.sh                                   # venv + pnpm full-stack launcher
skillsynth seed                                 # seed dev database (~1,109 rows)
skillsynth doctor --strict                      # gate: deps/AI/model/db all OK
```

## Environment Variables Read by Code
| Variable | Required | Default | Consumed by |
|----------|----------|---------|-------------|
| MODE | No | dev | database.py, config/, middlewares (dev=SQLite, prod=PostgreSQL + CSRF/HSTS-preload/CSP strict) |
| HOST / PORT | No | 127.0.0.1 / 8000 | backend/cli.py `run` (+ legacy run.py); --host/--port flags override |
| DATABASE_URL | prod | — | database.py (PostgreSQL) |
| DB_POOL_SIZE / DB_MAX_OVERFLOW / DB_POOL_TIMEOUT | No | 10 / 20 / 30 | database.py |
| SECRET_KEY | prod (mandatory) | dev fallback | config/app_settings.py (JWT signing) |
| ADMIN_EMAIL / ADMIN_PASSWORD | No | admin@skillsynth.io / unset | main.py lifespan admin autoseed |
| PASSWORD_PEPPER | No | empty | auth_service password hashing |
| REDIS_URL | prod optional | in-memory | limiter.py rate-limit storage |
| AI_ENABLED / AI_MODEL_PATH / AI_N_GPU_LAYERS / AI_N_CTX / AI_TEMPERATURE / AI_REPEAT_PENALTY / AI_TOP_P / AI_MAX_NEW_TOKENS | No | false / src/data/Llama-3.2-3B-Instruct-Q6_K.gguf / -1 / 4096 / 0.3 / 1.15 / 0.95 / 700 | llm_engine.py + routers/ai.py (ADR-015) |

Frontends read `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000/api`) from their env files.

Note: `skillsynth run` launches the full stack (backend + both Next frontends) and is cross-platform — on Windows it uses `pnpm.cmd` discovery and `taskkill`/process-group teardown, on POSIX it uses session groups + `killpg`; the AI_* env block seeds the file-backed runtime AI setting (ADR-015 §8).

Note: `.env.example` also lists legacy keys (SENDGRID_API_KEY, GITHUB_TOKEN). Current backend code does not consume these; they remain only as placeholders. The dead Phase-4 LLM blocks (LLM_*/OPENAI_*/OLLAMA_*, VECTOR_*/EMBEDDING_*) and the docker ollama service were removed — the local model is configured via the AI_* block above (ADR-015).

## Rules
1. pnpm is the only package manager for both frontends
2. Backend always starts from repo root via `skillsynth run`, `./skillsynth`, or legacy `python run.py` (all inject src/ into PYTHONPATH)
3. MODE=prod without SECRET_KEY or DATABASE_URL refuses to start
4. Schema bootstrap is DDL (`src/migrations/003_reduced_schema.sql`) + create_all + seed_v3.py — no migration framework
5. CORS origins are fixed per mode in config/app_settings.py (dev: localhost:3000)

## Examples
- Fresh dev machine: venv → pip install → seed_v3.py → run.py → pnpm dev in each frontend
- Single-node server: docker compose up -d behind a reverse proxy terminating TLS

## Edge Cases
- Port conflicts on 8000/3000/3001 → set PORT or stop the conflicting process
- Frontend cannot reach backend → verify NEXT_PUBLIC_API_BASE_URL matches the deployed API origin

## Failure Cases
- Missing SECRET_KEY with MODE=prod → immediate startup error (by design)
- PostgreSQL unreachable → uvicorn boots but every request fails; check DATABASE_URL

## Recovery Procedures
1. Validate env with the table above, restart processes
2. Rebuild containers after dependency changes: docker compose up -d --build

## Refactoring Strategy
- Keep Compose as the single deployment artifact; add services only when code consumes them
- Prune legacy keys from .env.example at each release
