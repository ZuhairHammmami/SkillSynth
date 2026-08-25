# Backend — DEPRECATED (absorbed into SS-EDS docs/07-backend/) — FastAPI

## Structure

```
src/backend/
├── main.py              # FastAPI app, startup hooks, middleware, SSE, exception handlers
├── database.py          # SQLAlchemy engine/session (SQLite dev / PostgreSQL prod)
├── models.py            # 10 ORM tables
├── schemas.py           # ~25+ Pydantic schemas
├── auth.py              # JWT create/verify, password hashing, get_current_user/admin
├── crud.py              # Generic CRUD helpers + specific data access
├── events.py            # SSE event manager + DB audit logging
├── gamification.py      # XP, streaks, achievements, levels
├── email_service.py     # SendGrid password reset emails
├── limiter.py           # Rate limiter (slowapi)
├── create_admin.py      # Standalone admin creation
└── routers/
    ├── auth_router.py        # /api/auth (register, login, profile, password mgmt)
    ├── paths_router.py       # /api/paths, /api/generate-path
    ├── options_router.py     # /api/wizard-options
    ├── assessments_router.py # /api/assessments, /api/assessment-results
    ├── progress_router.py    # /api/steps, /api/progress, /api/gamification
    ├── analytics_router.py   # /api/analytics (dashboard, skill-growth, velocity, etc.)
    └── admin_router.py       # /api/admin (CRUD for all entities, reports, audit)
```

## Critical: Import Convention

`run.py` adds `src/` to `sys.path`. Always use:
```python
from backend import models      # ✓ correct
from backend.database import get_db
from backend.routers.auth_router import router
# NOT:
from src.backend import models  # ✗ wrong
```

## Database Models (10 tables)

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `profiles` | email (unique), hashed_password, is_admin, role_id (FK→roles), skill_profile (JSON), total_xp, level, streak fields, achievements (JSON), preferences (JSON) | → paths (1:N), → completions (1:N), → assessment_results (1:N), → role (N:1) |
| `roles` | name (unique), permissions (JSON) | → profiles (1:N) |
| `categories` | name (unique) | — |
| `skills` | name (unique), difficulty_level, icon, color, category_ids (JSON), prerequisite_ids (JSON), resource_ids (JSON) | — |
| `job_roles` | title (unique), career_field, skill_ids (JSON) | — |
| `resources` | title, url, type, is_free, is_official, author_or_platform, language | — |
| `assessments` | title, assessment_type, questions (JSON) | → assessment_results (1:N) |
| `paths` | profile_id (FK), title, description, total_estimated_hours/weeks, goal_job_role, status, skill_ids (JSON) | → owner (N:1), → steps (1:N) |
| `path_steps` | path_id (FK), step_number, title, content, resource_ids (JSON), assessment_ids (JSON) | → path (N:1), → completions (1:N) |
| `step_completions` | profile_id (FK) + step_id (FK) = **composite PK**, completed_at | → profile (N:1), → step (N:1) |
| `assessment_results` | profile_id (FK), assessment_id (FK), score, total_questions, responses (JSON) | → profile (N:1), → assessment (N:1) |
| `events` | profile_id (FK nullable), category, action, entity_type, entity_id (nullable), data (JSON), ip_address | → profile (N:1) |

**Key**: Many-to-many uses JSON arrays on the parent (e.g., `skill_ids` on job_roles, `prerequisite_ids` on skills). No junction tables.

## Routers Summary

| Router | Prefix | # Endpoints | Auth |
|--------|--------|-------------|------|
| Auth | `/api/auth` | 10 | Mixed (register/login public, rest JWT) |
| Paths | `/api` | 9 | JWT |
| Wizard Options | `/api` | 1 | Public |
| Assessments | `/api` | 2 | Mixed |
| Progress | `/api` | 4 | JWT |
| Analytics | `/api/analytics` | 5 | JWT |
| Admin | `/api/admin` | 30+ | Admin-only |

## Pydantic Schemas

~25+ schemas in `schemas.py` + inline schemas in `auth_router.py`. Key patterns:
- `ProfileCreate` validates password: min 8 chars, ≥1 uppercase, ≥1 digit
- `Path` response includes `steps: list[PathStep]` each with `is_computed` flag
- `GeneratePathInput` uses nested `DetailedPreferences`
- Admin schemas: `AdminCreateUser`, `AdminCreateRole`, `AdminUpdateRole`

## Event System

- **SSE endpoint**: `GET /api/events` — streams real-time events to authenticated clients
- **Auth**: Supports Bearer token, query param token, or `authToken` cookie
- **Keepalive**: 30s ping interval
- **Events fired**: `step_completed`, `step_reverted`, `path_regenerated`, `assessment_completed`
- **Audit logging**: All events persisted to `events` table with `category="audit"` or `"learning"`

## Startup Sequence

1. Create all DB tables (`Base.metadata.create_all`)
2. Auto-create admin from `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars (if `ADMIN_PASSWORD` set)
3. Attach rate limiter to `app.state`

## Exception Handling

- `RateLimitExceeded` → 429
- `HTTPException` → status + detail JSON
- `RequestValidationError` → 422 (safe-serialized)
- Generic `Exception` → 500 (logged)
