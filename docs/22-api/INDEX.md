# SS-EDS: API

## Purpose
Document every FastAPI endpoint — 63 operations across 49 paths (verified from OpenAPI) — grouped by router, with auth requirements, rate limits, and token lifetimes. JWT access tokens only; there is no refresh endpoint.

## Responsibilities
- Maintain the authoritative endpoint inventory
- Document request/response schemas (Pydantic DTOs in dto/)
- State auth and rate-limit rules per group

## Inputs
- Router modules (src/backend/routers/)
- DTO definitions (src/backend/dto/)

## Outputs
- This specification
- Live OpenAPI/Swagger at /docs on :8000

## Dependencies
- 07-backend (implementations)
- 14-security (auth/rate limits)
- 08-frontend / 09-admin (consumers)

## Sequence: Request Lifecycle
```
Client → middleware (CORS → compression → security headers → CSRF[prod])
→ rate limiter → router → get_current_user/require_admin → DTO validation
→ service → repository → DB → JSON response
```

## Endpoint Inventory (63 operations / 49 paths)

### Authentication — /api/auth/* (7 paths / 8 ops)
| Method & Path | Auth | Notes |
|---------------|------|-------|
| POST /api/auth/register | public | 5/min; creates student account |
| POST /api/auth/token | public | 10/min; form-encoded login → {access_token} |
| GET /api/auth/me · PUT /api/auth/me | Bearer | read/update own profile |
| POST /api/auth/change-password | Bearer | current password required |
| POST /api/auth/forgot-password | public | 3/min; issues 30-min signed reset token |
| POST /api/auth/reset-password | public | 3/min; consumes reset token |
| POST /api/auth/sse-token | Bearer | 5-min SSE stream token |

### Learning Engine — /api/learning/* (3 paths / 3 ops, Bearer)
GET graph (prereq DAG nodes+edges) · GET gaps (skill-gap analysis) · POST generate (path generation alias)

### Paths & Progress — /api/* via paths.py (7 paths / 9 ops, Bearer)
POST /generate-path/ (wizard scoring → path) · GET /paths/ · GET|PUT|DELETE /paths/{path_id} (owner-scoped) · POST /steps/{step_id}/complete · POST /steps/{step_id}/undo-complete · GET /progress/dashboard

### Wizard Options — GET /api/wizard-options (1 op, public)
Job roles + preference literals for the wizard.

### Assessments — /api/assessments/* (3 paths / 3 ops, Bearer)
GET /{skill_id}/questions · GET /role/{job_role_title} · POST /submit (scores → user_skills proficiency 0–5)

### Analytics — /api/analytics/* (4 paths / 4 ops, Bearer)
GET dashboard · skill-growth · path-progress/{path_id} · learning-history

### Admin — /api/admin/* (19 paths / 30 ops, require_admin + admin limiter 60/min)
| Resource | Operations |
|----------|-----------|
| users | GET list · POST · PUT {id} · DELETE {id} |
| skills | GET · POST · PUT {id} · DELETE {id} (?force=true bypasses the 409 dependents census) |
| categories | GET · POST · PUT {id} · DELETE {id} (?force=true) |
| resources | GET · POST · PUT {id} · DELETE {id} |
| job-roles | GET · POST · PUT {id} · DELETE {id} (?force=true) |
| assessments | GET list · DELETE {id} |
| paths | GET (admin view) |
| events | GET feed (activity_log) |
| backups | GET list · POST create |
| db-inspector | GET table/row browser |
| feature-flags | GET configuration view |
| reports | GET aggregated · GET system-health |

Restricted deletes (skills/categories/job-roles): dependents present → **409 + census** unless `?force=true` (ADR-014).

### Realtime — /api/realtime/* (2 paths / 2 ops, token auth)
GET events (user SSE stream) · GET admin/events (admin SSE channel, ?category= filter)

### Root app routes (main.py, 4 ops)
GET / (health banner) · GET /api/public/stats (public, 30s inline cache) · GET /api/auth/csrf (prod CSRF handshake) · GET /api/events (SSE alias of /api/realtime/events)

## Request/Response Examples
```
POST /api/auth/token        Body: grant_type=password&username=<email>&password=***
→ 200 {"access_token": "...", "token_type": "bearer"}

POST /api/generate-path/    Header: Authorization: Bearer <jwt>
→ 200 PathDetailOut {id, title, steps:[...]}

DELETE /api/admin/skills/12 → 409 {"detail": {"message": "...", "dependents": {...}}}  # per-table counts
DELETE /api/admin/skills/12?force=true → 200                      # cascading removal
```

## Rules
1. All protected endpoints require `Authorization: Bearer <access JWT>`; access tokens live 24h (`ACCESS_TOKEN_EXPIRE_MINUTES = 60*24`) and renewal is re-authentication
2. Admin endpoints additionally require `users.is_admin` (require_admin dependency)
3. Rate limits: global 100/min · auth 10/min · register 5/min · forgot/reset 3/min · admin 60/min
4. Error codes: 400 validation/FK-miss/cycles · 401 unauthenticated · 403 non-admin · 404 missing · 409 conflicts (rename uniqueness on updates, restricted deletes, IntegrityError) · 422 malformed payload · 429 rate-limited
5. All responses JSON except SSE streams (text/event-stream)

## Failure Cases
- Expired/invalid token → 401
- Duplicate rename differing only by case on PUT → 409
- Missing FK reference in payload → 400 before persistence

## Recovery Procedures
1. Consult /docs for the live schema
2. Confirm backend reachability on :8000; inspect the failing response body for detail
