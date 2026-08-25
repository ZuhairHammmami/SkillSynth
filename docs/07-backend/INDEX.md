# SS-EDS: Backend

## Purpose
Document the FastAPI backend — 20-layer Clean Architecture, 91 files, ~83 routes across 9 routers (problems_router removed). Implements all business logic, data access, auth, real-time events, caching, and admin functionality.

## Responsibilities
- Serve all API endpoints (~83) via 9 routers
- Enforce Clean Architecture layers (Router → Service → Repository → Entity)
- Manage authentication (JWT, refresh token rotation, account lockout)
- Handle real-time events (SSE + WebSocket)
- Provide caching (`@cached` decorator, Redis/SQLite fallback)
- Maintain audit logging and telemetry

## Inputs
- API specifications (22-api)
- Database schema (10-database, 32 tables)
- Security requirements (14-security)

## Outputs
- FastAPI application on :8000
- OpenAPI/Swagger UI at /docs
- SSE event streams at /api/events
- Audit logs in events table

## Dependencies
- 10-database (SQLAlchemy entities, connection pool)
- 14-security (JWT, rate limiting, CSRF)
- 22-api (router endpoints)
- 23-events (SSE publishing)

## Backend Structure (20 layers, 91 files)
```
src/backend/
├── main.py              # FastAPI app, startup, middleware, 10 routers, exception handlers
├── database.py          # SQLAlchemy engine (SQLite dev / PostgreSQL prod), pool_size=10
├── limiter.py           # Rate limiter (100/min global, 10/min auth, 60/min admin)
├── routers/ (10 files)  # Thin handlers, no business logic
├── services/ (13 files) # Business logic, no SQL
├── repositories/ (9)    # Data access (SQLAlchemy only)
├── entities/ (11)       # SQLAlchemy models (one per file)
├── dto/ (12 files)      # Pydantic request/response schemas
├── validators/          # Input validation (password_validator.py)
├── policies/            # Authorization (auth_policy.py)
├── middlewares/         # Security, CSRF, Compression
├── events/              # SSE publisher + event publishers
├── commands/            # CQRS command handlers
├── queries/             # CQRS query handlers
├── cache/               # @cached / @invalidate_cache decorators
├── config/              # App settings (CORS, DB, secrets)
├── mappers/             # Entity<->DTO mapping
├── scheduler/           # Background tasks (placeholder)
├── metrics/             # Prometheus metrics (placeholder)
├── telemetry/           # OpenTelemetry (placeholder)
├── exceptions/          # Custom exception classes
└── tests/               # Test directory
```

## Router Directory (9 routers — problems_router removed)
```
auth_router.py      → /api/auth/*        (10 endpoints: register, login, profile, password)
paths_router.py     → /api/paths/*       (8 endpoints: CRUD, generate, regenerate)
options_router.py   → /api/wizard-options (1 endpoint: job roles, preferences)
assessments_router.py → /api/assessments/* (2 endpoints: questions, submit)
progress_router.py  → /api/steps/*       (4 endpoints: complete, undo, dashboard)
analytics_router.py → /api/analytics/*   (5 endpoints: dashboard, growth, velocity)
learning_router.py  → /api/learning/*    (7 endpoints: graph, generate, analyze, gaps)
realtime_router.py  → /api/realtime/*    (3 REST + 1 WebSocket: events, notify, broadcast, ws)
admin_router.py     → /api/admin/*       (35 endpoints: CRUD for all entities, reports, audit)
```

## API Performance (dev mode)
| Endpoint | Latency |
|----------|---------|
| /api/auth/me | 3.5ms |
| /api/paths/ | 17.7ms |
| /api/analytics/dashboard | Learning engine |
| /api/learning/graph | Graph data |
| /api/realtime/events | SSE streaming |

## Import Convention
```python
# Always use backend prefix (never src.backend):
from backend.services.auth_service import AuthService
from backend.repositories.profile_repository import ProfileRepository
from backend.entities.profile import Profile
from backend.dto.profile import ProfileCreate
from backend.policies.auth_policy import get_current_user
# run.py adds src/ to sys.path
```

## Rules
1. Imports: `from backend.xxx import yyy` — never `src.backend`
2. All endpoints return JSON. No HTML responses.
3. Services must have fallback values — never throw to caller
4. Router handlers are thin — delegate to services immediately
5. All files <300 lines, all functions <40 lines

## Examples
- Auth: Login → check lockout → verify bcrypt → create JWT → log audit
- Paths: Generate → validate input → LearningEngine → topological sort → DB persist
- SSE: Endpoint → decode JWT → event_generator → heartbeat every 30s

## Edge Cases
- DB mode switching (dev=SQLite, prod=PostgreSQL) via MODE env var
- JWT with SAME logging side effects (doesn't re-hash on every call)
- SSE queue full → message dropped, logged as warning

## Failure Cases
- Database unreachable → 500 with logged traceback
- JWT decode failure → 401 Unauthorized
- Rate limit exceeded → 429 with Retry-After

## Recovery Procedures
1. Restart FastAPI via `python run.py` (auto-reload in dev)
2. Check database connectivity and pool status
3. Verify SECRET_KEY and ADMIN_EMAIL env vars

## Refactoring Strategy
- Extract remaining inline CRUD from routers into services
- Add telemetry (OpenTelemetry) for all service calls
- Implement scheduler for periodic cache warming
