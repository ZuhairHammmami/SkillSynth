# SS-EDS: Module Boundaries

## Purpose
Define what each backend layer and frontend app may depend on. Dependency direction is one-way; crossing rules below are enforced by review and kept simple enough to check by reading imports.

## Responsibilities
- Fix the allowed import direction across the 8 backend layers
- Separate the two frontend apps from the backend (HTTP only)
- Prevent circular imports

## Inputs
- src/backend layout (8 layer directories + main.py/database.py/limiter.py)
- src/frontend and src/admin-app layouts

## Outputs
- Boundary map and import rules (below)

## Dependencies
- 06-architecture (layer inventory this document constrains)
- 07-backend / 08-frontend / 09-admin (implementations)

## Backend Boundaries
```
main.py ──────────────▶ routers/ ──▶ services/ ──▶ repositories/ ──▶ entities/
   │                       │             │                                ▲
   ├─▶ middlewares/        │             ├─▶ services/catalog_integrity.py┤
   ├─▶ config/             ├─▶ policies/ │                                │
   └─▶ events/ ◀───────────┴─────────────┘        (integrity helpers)     │
dto/ ◀── imported by routers + services            entities/ ◀── repositories
```
| Layer | May import | Must not import |
|-------|-----------|-----------------|
| routers/ | dto, policies, services, error_mapping | repositories, entities directly |
| services/ | dto, repositories, other services (catalog_integrity), events | routers |
| repositories/ | entities only | services, routers |
| policies/ | config, identity repository | routers, services |
| dto/ | nothing internal (Pydantic only) | everything |
| events/, middlewares/, config/ | stdlib/fastapi/config only | higher layers |

Removed layers (no re-creation without an ADR): mappers/, validators/, commands/, queries/, cache/, infrastructure/.

## Frontend Boundaries
```
src/frontend/src/          src/admin-app/src/
├── app/      (routes)     ├── app/           (routes incl. categories/, job-roles/)
├── shared/   (ui, lib)    ├── shared/
├── i18n/     (ar/en)      └── (English-only, no i18n runtime)
├── types/
└── middleware.ts
```
1. Student app (:3000) and admin app (:3001) never import from each other — duplication is accepted at this boundary
2. Neither frontend imports Python; all coupling is HTTP + JSON key contracts (frozen per 27-analytics)

## Sequence: Cross-Boundary Call
```
app/(dashboard)/page.tsx → shared/lib api client → fetch :8000/api/analytics/dashboard
→ router/analytics.py → analytics_service → learning_repository → entities → SQLite
```

## Rules
1. Python imports are always `from backend.xxx import yyy` — run.py injects src/ into sys.path
2. No layer skips the layer below it (routers never touch repositories)
3. SSE publishing goes through events/publisher.py — no direct Response streaming in services
4. Admin authorization is checked only in policies/require_admin, never inline in handlers
5. Zero circular imports: `python -c "import backend.main"` under PYTHONPATH=src must succeed
6. No file >300 lines, no function >40 lines

## Examples
- Allowed: services/admin_service.py importing repositories/catalog_repository.py
- Violation: routers/auth.py importing repositories/identity_repository.py directly (must go through auth_service)

## Edge Cases
- Shared DTO shape between two routers → defined once in dto/, both import it
- Integrity helpers used by multiple services → they live in services/catalog_integrity.py, not a new layer

## Failure Cases
- Circular import surfaces as partial-module ImportError at startup → break the cycle by moving shared code down a layer

## Recovery Procedures
1. Draw the offending import on the map above, find the lowest legal home, move the code

## Refactoring Strategy
- Add an import-linter CI check when violations exceed one per quarter
