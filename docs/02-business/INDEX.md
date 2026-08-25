# SS-EDS: Business

## Purpose
Document the operational model for SkillSynth: self-hosted deployment topology (FastAPI + Next.js on SQLite/PostgreSQL), cost drivers, and licensing posture. No managed-cloud dependency is assumed.

## Responsibilities
- Define the deployment model (self-hosted Docker Compose; single VPS or equivalent)
- Track operational cost drivers (hosting, optional LLM keys)
- Document data ownership and export expectations

## Inputs
- Infrastructure constraints (17-deployment)
- Hosting cost reports
- Licensing decisions (docs/41-decision-records/)

## Outputs
- Deployment topology description
- Cost-driver inventory

## Dependencies
- 17-deployment (build/run commands, Docker files)
- 01-product (feature scope determines cost surface)
- 14-security (compliance requirements)

## Sequence: User Onboarding Flow
```
Visit landing → Register → Assessment → Wizard → Generated Path → Step Completion → Analytics
```

## State Diagram: Environment Lifecycle
```
[dev: SQLite + uvicorn :8000] → [staging/prod: PostgreSQL via DATABASE_URL]
        ↑                              ↓
        └──────── re-seed (seed_v3.py) ┘
```

## ERD References
- users — account records; activity_log — audit trail (billing analytics not implemented)

## Rules
1. Core learning engine is free of external service dependencies — FastAPI + SQLite runs offline
2. Production requires only `MODE=prod`, `SECRET_KEY`, and `DATABASE_URL` (PostgreSQL)
3. No vendor lock-in: schema truth is portable SQL DDL (`src/migrations/003_reduced_schema.sql`); backups via POST /api/admin/backups
4. Optional integrations (LLM keys in .env.example) are not consumed by current backend code

## Examples
- Full stack on one machine: `docker compose up -d` starts backend :8000, student frontend :3000, admin app :3001
- Minimal dev setup: `python run.py` with SQLite + `seed_v3.py` (~1,100 rows)

## Edge Cases
- MODE=prod without DATABASE_URL → startup error (by design)
- SQLite file locked by another process → connection failure; restart the process

## Failure Cases
- Hosting budget overrun → scale down to single-node Docker; no per-service cloud bills exist
- Disk exhaustion from backups → prune the backup directory served by GET /api/admin/backups

## Recovery Procedures
1. Restore from a backup artifact produced by POST /api/admin/backups
2. Re-run seed_v3.py against a fresh database if no backup exists

## Refactoring Strategy
- Keep the operational footprint at one compose file; add services only when code consumes them
- Review .env.example each release and delete variables no code reads
