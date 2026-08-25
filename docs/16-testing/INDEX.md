# SS-EDS: Testing

## Purpose
Document the verification suite: 143 backend pytest tests across 11 files against an isolated temporary SQLite database (conftest-built per run; dev DB untouched), plus TypeScript type-check, ESLint, and production builds for both frontends.

## Responsibilities
- Maintain the pytest suite in repo-root `tests/` (pytest + httpx)
- Guarantee isolation: every run builds a temp DB from seed_v3 data via conftest.py
- Run `tsc --noEmit` (0 errors) for src/frontend and src/admin-app
- Run `next lint` and production builds as merge gates
- Verify schema parity with tools/verify_schema.py

## Inputs
- Feature code changes
- API contracts (Pydantic DTOs)

## Outputs
- Pass/fail evidence for every layer
- Coverage of auth, catalog integrity, learning guards, assessments, analytics, admin CRUD, realtime, schema

## Dependencies
- Backend suite at tests/ (requirements.txt declares pytest + httpx)
- 08-frontend / 09-admin build pipelines
- 10-database (verify_schema.py)

## Sequence: Pre-Merge Verification
```
PYTHONPATH=src python -m pytest tests/ -q        → 143 passed?
cd src/frontend  && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
```

## Sequence: Test Execution
```
PYTHONPATH=src python -m pytest tests/ -q
  → conftest.py creates an isolated temp SQLite DB (seeded from seed_v3 data; dev DB never touched)
  → 143 tests collected across 11 files
  → temp DB discarded after the session
```

## Current Test State
| Component | Status | Details |
|-----------|--------|---------|
| Backend tests | ✅ 143/143 | isolated temp SQLite per run |
| Frontend type-check + lint + build | ✅ pass | src/frontend |
| Admin app type-check + build | ✅ pass | src/admin-app |
| Schema verifier | ✅ SCHEMA MATCH | tools/verify_schema.py |

## Test Files (tests/, counts verified via --collect-only)
| File | Tests | Area |
|------|-------|------|
| test_admin.py | 22 | admin CRUD, backups, reports, restricted deletes |
| test_catalog_integrity.py | 20 | rename uniqueness, cycles, FK validation → 400/409 |
| test_catalog.py | 19 | catalog reads/writes |
| test_auth.py | 17 | register/login/me, lockout, password flows |
| test_learning.py | 15 | graph, gaps, generation |
| test_assessments.py | 13 | questions, role sets, submit scoring |
| test_integrity.py | 11 | cascade matrix + restricted deletes |
| test_analytics.py | 8 | dashboard, growth, history |
| test_realtime.py | 7 | SSE streams, event emission |
| test_schema.py | 7 | DDL/ORM parity |
| test_learning_guards.py | 4 | ownership/guard rails |

## Available Verification Commands
```bash
PYTHONPATH=src python -m pytest tests/ -q      # 143 tests, isolated temp DB
cd src/frontend && pnpm type-check             # tsc --noEmit
cd src/frontend && pnpm lint                   # next lint
cd src/frontend && pnpm build                  # type-check + next build
cd src/admin-app && pnpm type-check && pnpm build
PYTHONPATH=src python tools/verify_schema.py   # prints SCHEMA MATCH
PYTHONPATH=src python seed_v3.py               # re-seed dev database (~1,100 rows)
```

## Rules
1. Tests always run against the conftest temp DB — never the dev skillsynth.db
2. All 143 must pass before any merge
3. New endpoints require tests in the matching file before merge
4. After schema edits: update DDL + entities, then verify_schema.py must print SCHEMA MATCH
5. Frontend commits require type-check + lint; merges require builds

## Examples
- Restricted delete: DELETE skill with children → expect 409 census (test_admin.py)
- Rename conflict: PUT duplicate name differing only by case → expect 409 (test_catalog_integrity.py)

## Edge Cases
- TypeScript strict mode catches null-safety issues pre-runtime
- ESLint flags hardcoded user-facing strings (i18n violations)

## Failure Cases
- Any pytest failure → merge blocked until fixed
- Build failure on a clean checkout → environment or missing-import bug

## Recovery Procedures
1. Read the failing assertion; fix implementation or test intent
2. Re-run the full suite — partial runs are not evidence

## Refactoring Strategy
- Keep one file per feature area to preserve the traceability table above
- Future candidates (require discussion): Vitest units, Playwright E2E, CI wiring
