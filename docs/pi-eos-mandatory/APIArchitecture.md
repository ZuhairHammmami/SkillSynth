# API Architecture

## Design Principles
- RESTful resource naming (/api/{resources})
- JWT Bearer auth on all protected endpoints
- Pydantic V2 validation on all inputs
- JSON responses only (no HTML from API)
- SSE for real-time events, WebSocket for bidirectional

## Base URL
- Dev: `http://localhost:8000`
- Prod: `https://skillsynth-api.render.com`

## Endpoint Summary (~85 total)
| Area | Endpoints | Auth |
|------|-----------|------|
| Auth | `POST /api/auth/{register,token,change-password,forgot-password,reset-password}`, `GET /api/auth/{me,csrf}` | Mixed |
| Paths | `GET/POST/PUT/DELETE /api/paths`, `/api/paths/{id}`, `POST /api/generate-path` | JWT |
| Wizard | `GET /api/wizard-options` | JWT |
| Assessments | `GET /api/assessments/{role}`, `POST /api/assessment-results` | JWT |
| Progress | `POST /api/steps/{id}/{complete,undo-complete}`, `GET /api/progress/dashboard` | JWT |
| Analytics | `GET /api/analytics/{dashboard,skill-growth,learning-history,learning-velocity}` | JWT |
| Learning | `GET /api/learning/{graph,analysis,time-estimate,skill-gaps,progress}`, `POST /api/learning/recommendations` | JWT |
| Realtime | `GET /api/realtime/events`, `WS /api/realtime/ws`, `POST /api/realtime/{notify,broadcast,admin/alert}` | JWT |
| Admin | 35 endpoints under `/api/admin/*` for CRUD, reports, audit, analytics | JWT + is_admin |

## Response Format
```json
{
  "data": { ... },
  "error": null
}
```
Error responses: `{"detail": "message"}` with appropriate HTTP status.

## Status Codes
| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Not authenticated |
| 403 | Forbidden (not admin) |
| 404 | Not found |
| 422 | Pydantic validation error |
| 429 | Rate limit exceeded |
| 500 | Internal error |

## Rate Limiting
| Scope | Limit |
|-------|-------|
| Global | 100 requests/min |
| Auth endpoints | 10 requests/min |
| Admin endpoints | 60 requests/min |
