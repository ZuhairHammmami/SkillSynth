# SS-EDS: Error Handling

## Purpose
Document the real error-handling surface: four exception handlers in src/backend/main.py, the integrity semantics in services/catalog_integrity.py, and the two Next.js error boundaries in the student app. Services return error tuples; routers map them to HTTP codes.

## Responsibilities
- Map service failures to 400/404/409 consistently (catalog_integrity.py)
- Provide a central IntegrityError → 409 safety net (main.py:115)
- Flatten Pydantic validation errors into one detail string (main.py:131)
- Render retryable full-page fallbacks via app/error.tsx + global-error.tsx

## Inputs
- Service result tuples (None/False + message) from services/
- SQLAlchemy IntegrityError from any commit
- RequestValidationError from DTO parsing
- slowapi RateLimitExceeded

## Outputs
- JSON {detail: string-or-object} responses (429/409/422/500)
- Localized boundary UI with a Retry button (i18n keys title/description/retry)

## Dependencies
- 07-backend (handlers live in main.py; semantics in catalog_integrity.py)
- 08-frontend (src/frontend/src/app/error.tsx, global-error.tsx)
- 22-api (status-code contract per endpoint)

## Handler Inventory (main.py)
| Handler | Trigger | Response |
|---------|---------|----------|
| rate_limit_exceeded_handler (:108) | slowapi limit breach | 429 {"detail": "Rate limit exceeded. Please try again later."} |
| integrity_conflict_handler (:115) | uncaught DB constraint breach | 409 {"detail": "Database conflict: the operation violates a data constraint."}; session rolled back by get_db teardown |
| validation_exception_handler (:131) | RequestValidationError | 422 {"detail": "msg1; msg2"} flattened |
| global_exception_handler (:140) | any Exception | 500 {"detail": "Internal server error"} — traceback logged, nothing leaked |

## Status Semantics (service layer → router mapping)
| Status | Condition | Source |
|--------|-----------|--------|
| 404 | Target entity missing (skill/path/step/resource/user not found or not owned) | routers check None returns |
| 400 | Unknown FK reference in payload; prerequisite cycle violation; malformed filter | ensure_* guards in services/catalog_integrity.py |
| 409 | Already-exists renames; restricted delete with dependents; uncaught IntegrityError net | catalog_integrity.py + main.py |
| Restricted deletes | DELETE skills/categories/job-roles with dependents returns **409** whose detail carries `dependents` (per-table counts) + an actionable `message` unless `?force=true` (ADR-014) |

## Sequence: Error Flow
```
Service raises/guards fail
  → expected case: service returns (None, msg) → router raises HTTPException(400|404|409)
  → unexpected DB constraint: IntegrityError propagates → main.py handler → 409
  → frontend fetch layer receives non-2xx → toast/error state
  → render crash (not fetch error) → app/error.tsx boundary → localized message + Retry
```

## Frontend Boundaries
| File | Scope | Behavior |
|------|-------|----------|
| src/frontend/src/app/error.tsx | Route segment errors | Localized heading/description + Retry (reset()) |
| src/frontend/src/app/global-error.tsx | Root layout crashes | Minimal html/body shell with retry |
Fetch failures do NOT hit boundaries — they surface as component-level error states.

## Rules
1. Routers never contain business conditionals beyond tuple unpacking → status mapping
2. Internal details (SQL, stack traces, driver text) never reach the client
3. Every 500 is logged server-side at error level with exc_info
4. Conflict payloads name the blocking dependents so the caller can decide on ?force=true
5. Boundary copy comes from i18n message files — no hardcoded strings

## Examples
- DELETE /api/admin/skills/12 with dependent path_steps → 409 with detail.dependents counts; ?force=true → 200 cascade
- POST /api/admin/job-roles/skill link creating a duplicate junction row slipping past guards → IntegrityError → 409 net

## Edge Cases
- Validation error inside an SSE stream handshake → normal 422 (stream not yet open)
- Error thrown inside error.tsx itself → global-error.tsx catches

## Failure Cases
- Missing guard added to a new endpoint → first line of defense is the 409 IntegrityError net, never silent corruption

## Recovery Procedures
1. Reproduce: PYTHONPATH=src python -m pytest tests/test_integrity.py tests/test_catalog_integrity.py -q
2. Inspect uvicorn logs for the warning line emitted by integrity_conflict_handler

## Refactoring Strategy
- Keep handlers thin; new failure classes belong in services with explicit mappings, not new global handlers
