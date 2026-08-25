# SS-EDS: Performance

## Purpose
Document performance targets (TTFB <100ms, LCP <1.5s), current benchmark measurements, caching strategy, bundle size budgets, and optimization patterns for SkillSynth.

## Responsibilities
- Maintain sub-100ms API response times for critical endpoints
- Enforce N+1 prevention pattern (batch-fetch + in-memory dict)
- Monitor and optimize bundle sizes (shared JS <150KB per route)
- Manage React Query caching strategy (staleTime, gcTime)
- Implement code splitting and lazy loading for heavy components
- Track and optimize Lighthouse scores

## Inputs
- Profiling data from development benchmarks
- Database query execution plans
- Lighthouse audit results
- Bundle analysis (webpack/next-bundle-analyzer)

## Outputs
- Performance budget document
- Index optimization recommendations
- Bundle analysis reports
- Caching configuration

## Dependencies
- 10-database (indexes, query optimization)
- 07-backend (CRUD optimization, response compression)
- 08-frontend (dynamic imports, code splitting)
- 24-caching (Redis/SQLite cache decorators)

## Sequence: Performance Optimization Flow
```
Profile (request timing) → Identify Bottleneck → Design Fix → Implement → Verify → Ship
    ↑                                                                          ↓
    └─────────────────────── Regression check ─────────────────────────────────┘
```

## Current Benchmarks (Dev Mode, Authenticated)
| Endpoint | Time | Target |
|----------|------|--------|
| /api/auth/me | 3.5ms | <10ms |
| /api/paths/ | 17.7ms | <30ms |
| /api/learning/graph | ~15ms | <30ms |
| /api/analytics/dashboard | ~25ms | <50ms |
| /api/admin/users | 9.4ms | <30ms |
| /api/admin/paths | 16.0ms | <30ms |
| /api/admin/categories | 5.0ms | <20ms |

## State Diagram: Budget Status
```
[Green (<60%)] → [Warning (60-80%)] → [Critical (80-95%)] → [Violation (>95%)]
```

## Bundle Size Targets
| Chunk | Current | Target |
|-------|---------|--------|
| Shared JS (all routes) | 234KB | <150KB gzipped |
| Main entry | ~120KB | <100KB |
| Admin routes | ~80KB | <60KB (lazy) |
| Analytics dashboard | ~60KB | dynamic import |

## Rules
1. No N+1 queries — batch-fetch all related data in single query
2. React Query: staleTime=30s, gcTime=5min, refetchOnWindowFocus=true
3. Dynamic import all heavy components (charts, admin, knowledge graph)
4. Bundle: keep shared JS under 150KB gzipped per route
5. Images: WebP format with next/Image optimization
6. Cache: immutable assets with hash-based filenames
7. API responses compressed via GzipMiddleware

## Examples
- N+1 fix: fetch all skill_categories in one query → dict mapping → O(1) lookup per profile
- Dynamic import: `dynamic(() => import('./AnalyticsDashboard'), { ssr: false })`
- Caching: `@cached(ttl=300)` decorator on expensive queries

## Edge Cases
- Cold database start on first request (SQLite warmup)
- SSE connections consuming server memory (per-user queue)
- Rate limiting causing perceived slowness under load
- Large knowledge graph response size

## Failure Cases
- N+1 query introduced → blocked in PR review
- Bundle exceeds budget → build warning in CI
- Memory leak from SSE connection pools → periodic cleanup
- Slow query under load → missing index identified

## Recovery Procedures
1. Run query profiling to identify slow queries
2. Add missing index or rewrite query with batch JOIN
3. Split large bundle with dynamic import boundaries
4. Monitor SSE connection count and queue sizes

## Refactoring Strategy
- Monthly Lighthouse audit on all routes
- Quarterly database query plan review
- Implement Redis caching layer for hot endpoints
- Add performance regression tests in CI pipeline
