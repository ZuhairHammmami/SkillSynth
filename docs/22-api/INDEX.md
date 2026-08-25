# SS-EDS: API

## Purpose
Document all FastAPI endpoints (55 operations across 45 paths (7 routers)) across 7 routers + inline app routes. Covers authentication, request/response schemas, and authorization requirements.

## Responsibilities
- Maintain endpoint documentation by category
- Define request/response schemas (Pydantic DTOs)
- Document authentication and authorization requirements
- Track API route status (functional, stubbed, planned)

## Inputs
- Backend router implementations (07-backend)
- Pydantic schema definitions (dto/)
- Authentication requirements (14-security)

## Outputs
- API specification (this document)
- OpenAPI/Swagger UI at /docs

## Dependencies
- 07-backend (router implementations)
- 14-security (auth requirements)
- 08-frontend (API client usage)

## Sequence: API Request Lifecycle
```
Client → HTTP → FastAPI → Middleware → Rate Limiter → Router → Auth Policy → DTO Validation → Service → Repository → DB → Response
```

## State Diagram: Endpoint Maturity
```
[Planned] → [Stubbed] → [Functional] → [Deprecated] → [Removed]
```

## Endpoint Summary (55 operations / 45 paths)

### Auth — /api/auth/* (10: register, login, profile, password, sse-token, reset)
Rate: register 5/min, login 10/min, forgot-password 3/min, reset 3/min.

### Paths — /api/paths/* (8: CRUD, generate, regenerate, skills update, analytics)
All JWT. POST /generate-path/ creates via LearningEngine; PUT/DELETE owned paths.

### Wizard — GET /wizard-options (1, public). Returns job roles, career fields, formats.

### Assessments — GET /assessments/{role}, POST /assessment-results (2, first public, second JWT).

### Progress — /api/steps/* (3: complete, undo-complete, dashboard) — all JWT. ~~gamification/profile~~ removed.

### Analytics — /api/analytics/* (5: dashboard, path-progress, skill-growth, learning-history, learning-velocity) — all JWT.

### ~~Problems — /api/problems/* (2: list with filters, detail) — all JWT.~~ **REMOVED**

### Learning Engine — /api/learning/* (7: graph, path/generate, analysis, recommendations, progress, time-estimate, skill-gaps) — all JWT except graph.

### Real-time — /api/realtime/* (3 REST + 1 WebSocket: events SSE, notify, broadcast, /ws) — SSE: JWT token, others: admin.

### Admin — /api/admin/* (35 endpoints, all admin-only)
Reports: user-activity, content-engagement, system-health, most-active-users, most-requested-skills, aggregated. CRUD: /users, /roles, /skills, /categories, /resources, /job-roles. System: /paths, /audit-log, /events, /events/stream (admin SSE), /analytics/overview.

### System (3, in main.py): GET / (public), GET /api/auth/csrf (public), GET /api/events (SSE JWT).

## Request/Response Examples
```
POST /api/auth/token
  Body: grant_type=password&username=email&password=***
  Response: {access_token: "...", token_type: "bearer", expires_in: 1440}

GET /api/paths/
  Header: Authorization: Bearer <token>
  Response: [{id: 1, title: "Python Dev", steps: [...], skills: [...]}]

POST /api/steps/{id}/complete
  Header: Authorization: Bearer <token>
  Response: {id: 1, profile_id: 1, step_id: 5, completed_at: "..."}
```

## Rules
1. All protected endpoints require Bearer JWT token
2. Auth tokens expire in 24h, refresh tokens in 30 days
3. Admin endpoints require admin JWT + is_admin=True
4. Rate limits: register 5/min, login 10/min, forgot-password 3/min, global 100/min
5. All responses are JSON — validation errors serialized safely

## Failure Cases
- Invalid token → 401
- Rate limit exceeded → 429
- Validation error → 422
- Internal error → 500

## Recovery Procedures
1. Check /docs for schema
2. Verify backend on :8000
3. Check network tab for error responses
