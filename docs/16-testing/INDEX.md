# SS-EDS: Testing

## Purpose
Document the current testing setup: 79/79 tests passing against an isolated temporary SQLite DB (created per session by conftest and seeded from seed_v3 data — the dev DB is never touched), TypeScript type-check (0 errors), ESLint (0 errors, 0 warnings), frontend build passes. Covers available verification commands and test infrastructure.

## Responsibilities
- Maintain the backend test suite (79 tests covering auth, catalog, learning, assessments, analytics, admin, realtime, schema) in repo-root `tests/`
- Guarantee test isolation: each pytest session builds its own temp SQLite DB seeded via seed_v3 logic
- Run TypeScript type-check (tsc --noEmit) with 0 errors
- Run ESLint (next lint) with 0 errors (0 warnings)
- Verify frontend build (type-check + next build)
- Track test gaps and document verification procedures

## Inputs
- Feature specifications
- API contracts (Pydantic schemas)
- UI component specifications

## Outputs
- Test results and coverage reports
- Verification command documentation
- CI/CD configuration requirements

## Dependencies
- Backend test suite at repo-root `tests/` (pytest + httpx, declared in requirements.txt)
- 08-frontend (type-check, lint, build)
- 44-test-scenarios (test case definitions)

## Sequence: Pre-Commit Verification
```
Code Change → pnpm type-check (tsc --noEmit) → 0 errors? → pnpm lint → 0 errors? → pnpm build → Pass? → Commit
                    ↓ fail                              ↓ fail               ↓ fail
                Fix types                          Fix lint              Fix build
```

## Sequence: Test Execution
```
PYTHONPATH=src python -m pytest tests/ -q
  → conftest creates an isolated temp SQLite DB (seeded from seed_v3 data; dev DB untouched)
  → 79 tests collected
  → Test auth endpoints (login, me, register)
  → Test CRUD flows, DB integrity, headers
  → Temp DB discarded after the session
  → 79/79 passed ✓
```

## Current Test State
| Component | Status | Details |
|-----------|--------|---------|
| Backend tests (pytest) | ✅ 79/79 passed | Isolated temp SQLite DB per session, seeded from seed_v3 |
| TypeScript type-check | ✅ 0 errors | tsc --noEmit (frontend + admin app) |
| ESLint | ✅ 0 errors | 3 font warnings (expected) |
| Frontend build | ✅ Passes | type-check + next build |
| Admin app build | ✅ Passes | type-check + next build (`src/admin-app`) |
| DB seed | ✅ Verified | `PYTHONPATH=src python seed_v3.py` (~1109 rows) |

## Available Verification Commands
```bash
PYTHONPATH=src python -m pytest tests/ -q    # 79 tests, isolated temp DB
cd src/frontend && pnpm type-check           # tsc --noEmit
cd src/frontend && pnpm lint                 # next lint (3 font warnings expected)
cd src/frontend && pnpm build                # type-check + next build
cd src/admin-app && pnpm type-check && pnpm build
python tools/verify_schema.py                # prints SCHEMA MATCH on success
PYTHONPATH=src python seed_v3.py             # Re-seed dev database
# Backend: source .venv/bin/activate && pip install -r requirements.txt && python run.py
```

## Manual Test Scripts
- npx ts-node src/scripts/test-path-resolver.ts (DAG logic)
- npx ts-node src/scripts/test-ui-rendering.ts (mastery page)
- npx ts-node src/scripts/test-notification-loop.ts (validation)
- npx ts-node src/scripts/test-db-connection.ts (Supabase)

## Rules
1. Before any frontend commit: pnpm type-check && pnpm lint
2. Before merge: pnpm build (type-check + build)
3. After backend changes: run `PYTHONPATH=src python -m pytest tests/ -q`
4. After DB changes: re-run `PYTHONPATH=src python seed_v3.py`, then `python tools/verify_schema.py`
5. Tests must always run against the isolated temp DB — never against the dev database
6. All tests must pass before deployment

## Examples
- pnpm type-check → "0 errors" exit code
- pnpm lint → 0 errors, 3 warnings (font loading)
- pnpm build → "✓ Compiled successfully" exit code

## Edge Cases
- TypeScript strict mode catches null/undefined issues at compile time
- ESLint catches hardcoded Arabic strings (i18n violations)
- Build fails on missing module imports vs. dev-mode success

## Failure Cases
- pnpm type-check fails → type errors must be resolved before commit
- ESLint errors > 0 → lint errors must be fixed (warnings are acceptable)
- Build fails → silent compilation error missed in development
- API test fails → regression introduced by backend changes

## Recovery Procedures
1. Fix type errors by adding proper type annotations
2. Fix lint errors by following ESLint rule suggestions
3. Run pnpm build locally to verify before push
4. Check API test output for specific failing assertion

## Refactoring Strategy
- Add Vitest for frontend unit tests
- Add pytest fixtures for cleaner API test setup
- Add Playwright for E2E tests
- Add pre-commit hooks (husky + lint-staged)
- Automate test execution in CI pipeline
