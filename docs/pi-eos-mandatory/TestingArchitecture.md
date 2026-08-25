# Testing Architecture

## Test Layers
| Layer | Tool | Location | Coverage |
|-------|------|----------|----------|
| Backend API | pytest + fastapi.TestClient | `tests/` | 67 tests, 100% passing |
| Frontend Types | tsc --noEmit | `src/frontend/` | 0 errors |
| Frontend Lint | next lint | `src/frontend/` | 0 warnings |
| Frontend Build | next build | `src/frontend/` | 24 routes, 0 errors |
| DB Integrity | pytest (test_db.py) | `tests/test_db.py` | 12 table, seed, structure tests |

## Test Categories
| Category | File | Tests |
|----------|------|-------|
| Auth | `test_auth.py` | register, login, profile, password change, forgot/reset, CSRF, SSE token |
| Admin | `test_admin.py` | CRUD (skills, categories, resources, roles, paths), auth guards, reports, analytics |
| Assessments | `test_assessments.py` | GET assessment, submit, edge cases (nonexistent role, unauthorized) |
| Database | `test_db.py` | Table count (32+), seed data validation, FK cascade, indexes, admin/demo users |
| Paths | `test_paths.py` | CRUD, generate, undo, analytics, authorization, wizard options |
| Skills | `test_skills.py` | Wizard options, progress dashboard, analytics (growth/history/velocity), learning graph |

## What's NOT Tested
- Frontend component rendering (no React Testing Library)
- E2E workflows (no Playwright/Cypress)
- SSE/WebSocket connections (no async test client)
- LLM integration (no mock provider)
- Performance/load testing (no k6/artillery)

## Running Tests
```bash
PYTHONPATH=src python -m pytest tests/ -v
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
```
