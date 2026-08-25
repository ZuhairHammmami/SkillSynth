# Backend Architecture

## 20-Layer Clean Architecture

| Layer | Directory | Purpose | Status |
|-------|-----------|---------|--------|
| 1 | `routers/` | HTTP handlers, no business logic | ✅ 9 routers, ~85 endpoints |
| 2 | `services/` | Business logic, no SQL | ✅ 13 services |
| 3 | `repositories/` | Data access, SQLAlchemy only | ✅ 9 repositories |
| 4 | `entities/` | SQLAlchemy models (one per file) | ✅ 11+ models |
| 5 | `dto/` | Pydantic request/response schemas | ✅ 10 files (Pydantic V2) |
| 6 | `validators/` | Input validation | ✅ Password validator |
| 7 | `policies/` | Authorization dependencies | ✅ Auth policy |
| 8 | `middlewares/` | Security, CSRF, Compression | ✅ 3 middlewares |
| 9 | `events/` | SSE publisher | ✅ Event generator |
| 10 | `commands/` | CQRS command handlers | ✅ Learning commands |
| 11 | `queries/` | CQRS query handlers | ✅ Learning queries |
| 12 | `cache/` | Caching decorators | ⬜ Empty |
| 13 | `config/` | App settings | ✅ CORS, DB, secrets |
| 14 | `mappers/` | Entity<->DTO mapping | ⬜ Empty |
| 15 | `infrastructure/` | Scheduler, metrics, telemetry | ⬜ Empty |
| 16 | `scheduler/` | Background tasks | ⬜ Empty |
| 17 | `metrics/` | Prometheus | ⬜ Empty |
| 18 | `telemetry/` | OpenTelemetry | ⬜ Empty |
| 19 | `exceptions/` | Custom exceptions | ⬜ Empty |
| 20 | `domain/` | Domain services | ⬜ Empty |

## Router Directory
| Router | Prefix | Endpoints |
|--------|--------|-----------|
| `auth_router.py` | `/api/auth/*` | 10 (register, login, profile, password) |
| `paths_router.py` | `/api/paths/*` | 8 (CRUD, generate, regenerate) |
| `options_router.py` | `/api/wizard-options` | 2 (wizard options) |
| `assessments_router.py` | `/api/assessments/*` | 2 (questions, submit) |
| `progress_router.py` | `/api/steps/*` | 4 (complete, undo, dashboard) |
| `analytics_router.py` | `/api/analytics/*` | 5 (dashboard, growth, velocity) |
| `learning_router.py` | `/api/learning/*` | 7 (graph, generate, analyze, gaps) |
| `realtime_router.py` | `/api/realtime/*` | 6 (SSE, WS, notify, broadcast) |
| `admin_router.py` (aggregate) | `/api/admin/*` | 35 (CRUD, reports, audit) |

## Import Convention
```python
from backend.services.auth_service import AuthService
from backend.repositories.profile_repository import ProfileRepository
```

## Construction
```python
# run.py
sys.path.insert(0, "src")
# All imports use: from backend.xxx import yyy
```
