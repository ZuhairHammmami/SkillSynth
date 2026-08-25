# SS-EDS: Module Boundaries

## Purpose
Document the module boundary definitions for SkillSynth, defining separation of concerns between backend, frontend, and services layers. Covers import rules, dependency direction, and encapsulation principles.

## Responsibilities
- Define module boundaries and their responsibilities
- Enforce dependency direction (layers import in one direction)
- Document acceptable cross-boundary communication patterns
- Prevent circular dependencies and architectural violations

## Inputs
- Architecture decisions (06-architecture)
- Backend structure (07-backend)
- Frontend structure (08-frontend)
- Services inventory (docs/SERVICES.md)

## Outputs
- Module boundary map
- Dependency graph
- Import rule documentation

## Dependencies
- 06-architecture (overall architecture)
- 07-backend (backend modules)
- 08-frontend (frontend modules)
- 12-realtime (cross-boundary events)

## Backend Module Boundaries
```
src/backend/
├── main.py              → Entry point, depends on all routers
├── routers/             → API handlers, depend on crud + auth + schemas
├── crud.py              → Data access, depends on models + database
├── models.py            → ORM models, depends on database
├── schemas.py           → Pydantic schemas, standalone
├── auth.py              → Auth logic, depends on models + database
├── events.py            → SSE events, depends on database
├── ~~gamification.py~~      → ~~Gamification logic~~ **REMOVED**
└── database.py          → Engine/session, standalone
```

## Frontend Module Boundaries
```
src/frontend/src/
├── app/                 → Pages (routes), depends on features + shared
├── features/            → Feature modules (auth, paths, admin, analytics)
├── shared/              → Shared components, hooks, lib, store
├── i18n/                → Localization config and messages
└── entities/            → TypeScript entity definitions
```

## Services Layer
```
src/services/
├── HybridLLMProvider.ts           → Standalone, no project imports
├── VectorSearchService.ts         → Standalone, DI interface
├── ProjectSubmissionService.ts    → Standalone, stubbed
├── shared/
│   ├── notification/              → NotificationService (not wired)
│   └── conflict-checker/          → ConflictCheckerService (pure functions)
```

## Sequence: Dependency Direction
```
Frontend Pages → Feature Hooks → Shared API Client → Backend API → Backend Router → CRUD → Models → Database
```

## Rules
1. Backend should not import from frontend
2. Frontend imports from services via @/services alias (crosses outside src/frontend/)
3. Services layer should not import from backend or frontend
4. Pages only import from features and shared (not directly from backend)
5. No circular dependencies between feature modules
6. Python imports: always `from backend import X` (not `from src.backend`)

## ERD References
- 12 database tables mapped by backend models.py

## Examples
- Correct: `pages/dashboard/page.tsx` imports from `@/features/paths/hooks`
- Correct: `api.ts` makes HTTP request to backend, never imports backend code
- Wrong: frontend component importing from `src/backend/` directly

## Edge Cases
- Type sharing between backend and frontend → duplicate entity definitions in src/entities/
- Shared validation logic → duplicated (not shared package yet)
- Services alias crosses project boundary → intentional design

## Failure Cases
- Circular import → Python: ImportError, TypeScript: runtime error
- Module boundary violation → architectural debt, hard to test
- Shared code duplicated → maintenance overhead

## Recovery Procedures
1. Identify violation by checking import graph
2. Extract shared logic to appropriate module
3. Update boundary documentation

## Refactoring Strategy
- Create shared types package for backend/frontend type consistency
- Convert services layer to proper microservices
- Add import boundary enforcement tool (e.g., dependency-cruiser)
- Document module boundaries with architecture tests
