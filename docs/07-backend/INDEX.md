# SS-EDS: Backend

## Purpose
Document the FastAPI backend — Clean Architecture with 9 layer directories under `src/backend/`, 7 mounted routers serving 49 paths / 63 operations, JWT-only auth, SSE-only realtime, and an inline 30s stats cache.

## Responsibilities
- Serve all API operations via thin router handlers
- Enforce layering: Router → Service → Repository → Entity
- Manage authentication (single 24h access JWT; renewal = re-authentication)
- Stream realtime events over SSE exclusively
- Audit actions into activity_log

## Inputs
- API specification (22-api)
- Schema truth (10-database, 15 tables)
- Security requirements (14-security)

## Outputs
- FastAPI application on :8000 (`python run.py`)
- OpenAPI/Swagger UI at /docs
- SSE streams at /api/realtime/events (+ /api/events alias)

## Dependencies
- 10-database (SQLAlchemy engine + entities)
- 14-security (JWT, rate limiting, CSRF, headers)
- 22-api (endpoint inventory)
- 23-events (SSE publishing)

## Backend Structure (`src/backend/`, counts exclude `__init__.py`)
```
main.py            # app factory, lifespan (create_all + admin autoseed), middleware, router mounting
database.py        # SQLAlchemy engine: MODE=dev→SQLite skillsynth.db, prod→DATABASE_URL (pooled)
limiter.py         # slowapi limiters: global 100/min, auth 10/min, admin 60/min (Redis store if REDIS_URL in prod)
routers/ (9)       # auth · learning · paths · assessments · analytics · admin · catalog_admin · realtime (+ error_mapping.py)
services/ (8)      # auth · catalog · catalog_integrity · learning · assess · wizard · analytics · admin
repositories/ (6)  # identity · catalog · learning · assess · engagement · integrity
entities/ (6)      # base.py + identity/catalog/learning/assessment/engagement modules → 15 tables
dto/ (4)           # auth · catalog · learning · admin (Pydantic)
policies/ (1)      # get_current_user + require_admin
middlewares/ (3)   # security headers · csrf (prod-only) · compression (gzip ≥1KB)
events/ (1)        # publisher.py — in-memory SSE pub/sub
config/ (1)        # app_settings.py — env vars, CORS, ACCESS_TOKEN_EXPIRE_MINUTES
```
Removed layers (no longer exist): mappers/, validators/, commands/, queries/, cache/, infrastructure/ — see ADR-013.

## Router Directory (7 mounted routers, 8 modules)
```
auth.py             /api/auth      register · token · me (GET/PUT) · change-password ·
                                   forgot-password · reset-password · sse-token     7 paths / 8 ops
learning.py         /api/learning  graph · gaps · generate                           3 / 3
paths.py            /api           generate-path/ · paths CRUD (list/get/put/delete) ·
                                   steps complete/undo · progress/dashboard ·
                                   wizard-options                                    7 / 9
assessments.py      /api           assessments/{skill_id}/questions · role/{title} · submit   3 / 3
analytics.py        /api/analytics dashboard · skill-growth · path-progress/{id} ·
                                   learning-history                                  4 / 4
admin.py            /api/admin     users CRUD · assessments (get/delete) · paths view ·
                                   events feed · backups · db-inspector ·
                                   feature-flags · reports/aggregated ·
                                   reports/system-health                            11 / 14
catalog_admin.py    /api/admin     skills/categories/resources/job-roles × CRUD      8 / 16
realtime.py         /api/realtime  events (user SSE) · admin/events (admin SSE)      2 / 2
main.py extras      /              root health · public/stats · auth/csrf · events alias   4 / 4
```

## Auth Model (JWT-only)
- Access token: HS256, `ACCESS_TOKEN_EXPIRE_MINUTES = 60*24` (config/app_settings.py); the API issues exactly one token kind per purpose — access, SSE stream, password reset
- SSE stream token: 5 minutes (POST /api/auth/sse-token)
- Password-reset token: 30-minute signed JWT, stateless single-use
- Account lockout: 5 failed logins → 15-minute cooldown

## Import Convention
```python
from backend.services.auth_service import AuthService          # never src.backend.*
from backend.repositories.identity_repository import IdentityRepository
from backend.policies.auth_policy import get_current_user, require_admin
# run.py injects src/ into sys.path before uvicorn starts
```

## Rules
1. Router handlers are thin — delegate to services immediately
2. Services never import SQLAlchemy session types beyond passing them through
3. All responses are JSON except SSE streams (text/event-stream)
4. Integrity errors funnel through one handler: FK miss → 400, rename conflict on update → 409, cycles → 400, IntegrityError → 409
5. All files <300 lines, functions <40 lines, docstrings mandatory

## Examples
- Login: POST /api/auth/token (form-encoded) → lockout check → bcrypt verify → JWT issue → activity_log entry
- Path generation: POST /api/generate-path/ → wizard scoring → Kahn topo sort → persist path/steps → emit path_generated SSE

## Edge Cases
- MODE=prod without SECRET_KEY → startup raises (config/app_settings.py)
- SSE queue full → event dropped, warning logged; client refetches on reconnect

## Failure Cases
- Database unreachable → 500 with logged traceback
- Invalid/expired token → 401; rate-limit breach → 429 with Retry-After

## Recovery Procedures
1. Restart via `python run.py` (auto-reload only when MODE=dev)
2. Verify DB file/DATABASE_URL and required env secrets

## Refactoring Strategy
- New domains add a service module, not a new layer
- Dead code is deleted outright with an ADR note
