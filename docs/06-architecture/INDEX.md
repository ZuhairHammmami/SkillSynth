# SS-EDS: Architecture

## Purpose
Document the SkillSynth system architecture: Clean Architecture backend (8 layer directories, 7 routers), two Next.js frontends, a strict-3NF 15-table database, request lifecycle, and deployment topology.

## Responsibilities
- Maintain layer boundaries and dependency direction
- Define communication patterns (HTTP + SSE; no other transports)
- Track architectural decisions (docs/41-decision-records/)

## Inputs
- Performance requirements (04-non-functional-requirements)
- Security constraints (14-security, OWASP Top 10)
- Schema truth (src/migrations/003_reduced_schema.sql)

## Outputs
- Architecture diagrams (docs/40-diagrams/)
- ADRs (docs/41-decision-records/, incl. ADR-013 schema reduction, ADR-014 restricted deletes)

## Dependencies
- 07-backend (implements the backend layers)
- 08-frontend / 09-admin (implement the clients)
- 10-database (15-table persistence)

## System Design
```
┌────────────────────────────┐   ┌────────────────────────────┐
│  Student Frontend :3000    │   │  Admin App :3001           │
│  Next.js 14, ar/en, RTL    │   │  Next.js, English-only     │
└─────────────┬──────────────┘   └─────────────┬──────────────┘
              │        HTTP + SSE (Bearer JWT) │
              └──────────────┬─────────────────┘
                             ▼
              FastAPI Backend :8000 (run.py → uvicorn)
              ┌─────────────────────────────────────┐
              │ Middlewares: CORS, Compression(1KB),│
              │ SecurityHeaders, CSRF (prod only)   │
              ├─────────────────────────────────────┤
              │ Routers (7): auth · learning · paths│
              │ · assessments · analytics · admin ×2│
              │ · realtime          49 paths / 63 op│
              ├─────────────────────────────────────┤
              │ Services (8): business logic        │
              │ Repositories (6): SQLAlchemy only   │
              │ Entities (5 modules): 15 ORM tables │
              └──────────────┬──────────────────────┘
                             ▼
                 SQLite (dev) / PostgreSQL (prod)
```

## Dependency Flow
```
Router (thin handler) → Service (business logic) → Repository (data access) → Entity (ORM model)
```

## Sequence: Request Lifecycle
```
Client → FastAPI middleware stack:
  1. CORSMiddleware
  2. CompressionMiddleware (gzip for bodies ≥1KB)
  3. SecurityHeadersMiddleware (CSP, HSTS, XFO)
  4. CSRFMiddleware (prod only, double-submit)
→ Rate limiter (slowapi: global 100/min, auth 10/min, admin 60/min)
→ Router match → auth policy (get_current_user / require_admin)
→ Pydantic DTO validation → Service → Repository → DB
→ JSON response (SSE text/event-stream on stream endpoints)
```

## State Diagram: Backend Startup
```
[Start] → load_dotenv → build engine (MODE selects SQLite/PostgreSQL)
  → lifespan: create_all (15 tables) + auto-create admin if ADMIN_PASSWORD set
  → attach middlewares → mount 7 routers → [Ready on :8000]
```

## Layer Directory (`src/backend/`)
```
routers/       9 files  — 8 router modules (+ error_mapping.py); admin split across admin.py + catalog_admin.py
services/      8 files  — auth · catalog · catalog_integrity · learning · assess · wizard · analytics · admin
repositories/  6 files  — identity · catalog · learning · assess · engagement · integrity
entities/      6 files  — base.py + 5 consolidated model modules (15 tables)
dto/           4 files  — auth · catalog · learning · admin (Pydantic schemas)
policies/      1 file   — get_current_user, require_admin (is_admin gate)
middlewares/   3 files  — security · csrf · compression
events/        1 file   — in-memory SSE pub/sub (publisher.py)
config/        1 file   — app_settings.py (env, CORS, token lifetime)
+ main.py, database.py, limiter.py
```
Removed layers (ADR-013 and earlier cleanups): mappers/, validators/, commands/, queries/, cache/, infrastructure/ — deleted as dead code or dissolved with their features.

## Rules
1. No business logic in routers; no SQL in services; repositories own all queries
2. Imports use `from backend.xxx import yyy` (run.py injects src/)
3. SSE is the only push channel — no second transport exists
4. Authorization is binary `users.is_admin` — no role/permission tables or per-permission dependencies exist
5. No file >300 lines, no function >40 lines
6. Schema changes must update the canonical DDL and pass tools/verify_schema.py

## Examples
- POST /api/generate-path/ → paths.py → learning_service.generate_path → learning_repository persist
- GET /api/admin/skills → catalog_admin.py (require_admin) → catalog_service → catalog_repository

## Edge Cases
- MODE=prod without DATABASE_URL → startup refuses to run
- SSE client disappears → queue cleaned up by the generator's finally block

## Failure Cases
- Repository raises IntegrityError → centralized handler maps it to 409
- FK reference missing at DTO level → validated to 400 before persistence

## Recovery Procedures
1. Check uvicorn logs for the traceback
2. Verify DB connectivity and MODE/DATABASE_URL values

## Refactoring Strategy
- Keep layer count fixed; new capability = new service module, not a new layer
- Any layer removal requires an ADR documenting what replaced it
