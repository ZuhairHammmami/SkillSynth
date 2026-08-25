# Architecture Overview

## System Architecture

```
Browser (RTL/Arabic UI)
    │
    ├── Next.js 14 (Frontend :3000)
    │   ├── App Router (24 routes, 3 groups)
    │   ├── React Query (server state)
    │   ├── Zustand (auth session)
    │   └── next-intl (i18n, AR/EN)
    │
    └── FastAPI (Backend :8000)
        └── 20-layer Clean Architecture
            ├── Routers (9 routers, ~85 endpoints)
            ├── Services (13 services, business logic)
            ├── Repositories (9 repositories, data access)
            └── Entities (11+ SQLAlchemy models)
                └── Database (SQLite dev / PostgreSQL prod)
```

## Layer Architecture
```
Router (thin handler, no logic)
  → Service (business logic, no SQL)
    → Repository (data access, SQLAlchemy only)
      → Entity (ORM model, one per file)
```

## Request Lifecycle
```
Client → Middleware (CORS, Security, Compression, CSRF)
  → Rate Limiter (100/min global)
  → Router match + Auth Policy (JWT decode)
  → Pydantic validation (DTO)
  → Service call (business logic)
  → Repository call (SQLAlchemy)
  → DB query (pooled connection)
  → JSON response
```

## Data Flow
- **HTTP**: REST API via FastAPI routers
- **SSE**: `/api/events` for real-time progress updates
- **WebSocket**: `/api/realtime/ws` for bidirectional comms
- **Cache**: React Query cache invalidation on SSE events

## Key Design Decisions
1. **Clean Architecture** — Strict 4-layer separation, no shortcuts
2. **Feature-Sliced Frontend** — Route groups isolate auth/student/admin
3. **Admin ≠ Student** — Two separate Next.js route groups, different layouts, data, permissions
4. **Deterministic Engine** — Kahn's topological sort, no LLM in path generation
5. **Arabic-First** — `dir="rtl"` default, Tajawal font, dynamic switching
