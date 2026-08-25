# SS-EDS: Architecture

## Purpose
Document the complete system architecture for SkillSynth: 20-layer Clean Architecture (FastAPI), request lifecycle, dependency flow, and deployment topology.

## Responsibilities
- Maintain architectural decision records and layer boundaries
- Define dependency flow (Router → Service → Repository → Entity)
- Document communication patterns (HTTP, SSE, WebSocket)
- Track architectural debt and migration plans

## Inputs
- Phase roadmap decisions
- Performance requirements (TTFB <100ms, LCP <1.5s)
- Security constraints (OWASP Top 10)

## Outputs
- Architecture diagrams (docs/40-diagrams/)
- ADRs (docs/41-decision-records/)
- Module boundary definitions (docs/49-module-boundaries/)

## Dependencies
- 07-backend (implements architecture)
- 08-frontend (implements architecture)
- 10-database (32-table 3NF persistence)

## System Design
```
┌──────────────────────────────────────────────────────────┐
│                    Browser (RTL/Arabic UI)                 │
└──────────────────┬───────────────┬───────────────────────┘
                   │               │
          ┌────────┴────┐   ┌──────┴────────┐
          │  Next.js    │   │  React Query  │
          │  (SSR/ISR)  │   │  + API Client │
          └──────┬──────┘   └──────┬─────────┘
                 │                 │
          ┌──────┴─────────────────┴──────────┐
          │        FastAPI Backend :8000        │
          │  ┌─────────────────────────────┐   │
          │  │  Middleware (CORS, Security, │   │
          │  │  Compression, CSRF)         │   │
          │  ├─────────────────────────────┤   │
          │  │  Routers (10 routers, ~85   │   │
          │  │  endpoints → services/      │   │
          │  ├─────────────────────────────┤   │
          │  │  Services (13 services)     │   │
          │  │  → business logic, no SQL   │   │
          │  ├─────────────────────────────┤   │
          │  │  Repositories (9 repos)     │   │
          │  │  → data access, SQLAlchemy  │   │
          │  ├─────────────────────────────┤   │
          │  │  Entities (11 models)       │   │
          │  │  → SQLAlchemy ORM models    │   │
          │  └─────────────────────────────┘   │
          │  20 layers, 91 Python files        │
          └──────────────┬──────────────────────┘
                         │
             ┌───────────┴────────────┐
             │  SQLite (dev)          │
             │  PostgreSQL (prod)     │
             │  Connection pool:      │
             │  pool_size=10,         │
             │  max_overflow=20       │
             └────────────────────────┘
```

## Dependency Flow
```
Router (thin handler, no logic)
  → Service (business logic, no SQL)
    → Repository (data access, SQLAlchemy only)
      → Entity (ORM model)
```

## Sequence: Request Lifecycle
```
Client → Nginx → FastAPI → Middleware stack:
  1. CORSMiddleware (allow origins)
  2. CompressionMiddleware (gzip >1KB)
  3. SecurityHeadersMiddleware (CSP, HSTS, XFO)
  4. CSRFMiddleware (prod only, double-submit)
  → Rate Limiter (global 100/min, auth 10/min, admin 60/min)
  → Router match
  → Auth Policy check (get_current_user / require_permission)
  → Pydantic validation (DTO layer)
  → Service call
  → Repository call
  → DB query (SQLAlchemy, pooled connection)
  → Response (JSON via mapper)
```

## State Diagram: Backend Startup
```
[Start] → Load .env → Init DB Engine (pool_size=10, max_overflow=20)
  → Create all tables (Base.metadata.create_all)
  → Auto-create admin (ADMIN_EMAIL/ADMIN_PASSWORD)
  → Attach middleware stack
  → Mount 10 routers
  → Attach exception handlers (429, 422, 401, 500)
  → [Ready on :8000]
```

## Layer Directory (20 layers)
```
routers/      services/   repositories/  entities/     dto/
validators/   policies/   middlewares/    events/       commands/
queries/      cache/      config/         mappers/      infrastructure/
scheduler/    metrics/    telemetry/      exceptions/   tests/
```

## Rules
1. No business logic in routers — thin handlers only
2. No SQL in services — repositories own all queries
3. All imports: `from backend.xxx import yyy` (run.py injects src/ into PYTHONPATH)
4. Every service must have a fallback — never throw
5. SSE for real-time, WebSocket for bidirectional
6. No file >300 lines, no function >40 lines

## Examples
- Routers call services, services call repositories, repositories use entities
- Cache layer (`@cached` decorator) wraps service calls with Redis/SQLite fallback
- Learning engine uses CQRS: commands/ + queries/ for path generation

## Edge Cases
- Both backends down → graceful degradation
- Database unreachable → read-only mode from cache
- SSE connection lost → React Query refetch

## Failure Cases
- Service returns error → fallback absorbs it, logs warning
- Kahn's algorithm detects cycle → skipped edges, warning
- Connection pool exhausted → queued, retry with backoff

## Recovery Procedures
1. Check FastAPI logs for stack trace
2. Verify database connectivity and connection pool
3. Check middleware and rate limiter state

## Refactoring Strategy
- Extract more services from monolithic routers
- Add event sourcing for critical domain events
- Migrate to full Redis-backed rate limiting in prod
