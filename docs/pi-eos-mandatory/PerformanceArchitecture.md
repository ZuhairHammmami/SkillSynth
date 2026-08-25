# Performance Architecture

## Budgets
| Metric | Target |
|--------|--------|
| API P95 Latency | <200ms |
| Auth P95 | <50ms |
| Frontend LCP | <1.5s |
| Frontend TTFB | <500ms |
| DB Query P95 | <30ms |
| Bundle Size | <250kB gzip |

## Optimizations Implemented
| Layer | Optimization | Status |
|-------|-------------|--------|
| Backend | Connection pooling (pool_size=10) | ✅ |
| Backend | Gzip compression (all responses >1KB) | ✅ |
| Backend | SQLAlchemy WAL mode + synchronous=NORMAL | ✅ |
| Backend | SQLite temp_store=MEMORY + cache_size=-8000 | ✅ |
| Frontend | React Query caching + stale-while-revalidate | ✅ |
| Frontend | Dynamic imports for heavy components | ✅ |
| Frontend | Code splitting per route (Next.js) | ✅ |
| Frontend | Font swap strategy (Tajawal via next/font) | ✅ |
| Frontend | Shared JS chunk ~234kB | ✅ |

## N+1 Prevention
- Batch queries in repositories (never loop with individual queries)
- `selectin` loading for relationship collections (User.roles)
- JOIN-based aggregations for dashboard data

## Caching Strategy
| Cache | TTL | Invalidation |
|-------|-----|--------------|
| React Query (paths) | 5 min | On SSE event + mutation success |
| React Query (skills) | 30 min | On admin CRUD mutation |
| React Query (analytics) | 1 min | On SSE metrics_refresh |
| SSE event queue | 100 events | FIFO drop when full |
