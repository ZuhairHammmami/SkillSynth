# SS-EDS: Performance

## Purpose
Document performance targets, current dev-mode benchmarks, the response-compression and inline-cache strategy, bundle discipline, and N+1 prevention for SkillSynth.

## Responsibilities
- Keep critical endpoints within their latency budgets
- Enforce the N+1 prevention pattern (batch-fetch + dict lookup)
- Serve gzip-compressed responses (bodies ≥1KB)
- Maintain React Query client caching defaults
- Track Lighthouse scores on UI changes

## Inputs
- Dev-mode request timings
- Query plans from services/repositories
- Lighthouse audits

## Outputs
- Benchmark table (this document, refreshed per release)
- Index recommendations feeding 10-database

## Dependencies
- 10-database (26 indexes, query patterns)
- 07-backend (compression middleware, inline stats cache)
- 24-caching (cache policy)

## Sequence: Performance Optimization Flow
```
Profile → Identify bottleneck → Fix (index / batch / cache) → Verify (pytest + manual timing) → Merge
```

## Current Benchmarks (Dev Mode)
| Endpoint | Time | Target |
|----------|------|--------|
| /api/auth/me | 3.5ms | <10ms |
| /api/paths/ | 17.7ms | <30ms |
| /api/admin/users | 9.4ms | <30ms |
| /api/analytics/dashboard | ~25ms | <50ms |

## State Diagram: Budget Status
```
[Green (<60%)] → [Warning (60–80%)] → [Critical (80–95%)] → [Violation (>95%)]
```

## Server-Side Levers (current reality)
| Lever | Implementation | Config |
|-------|----------------|--------|
| Inline TTL cache | `_stats_cache` dict in main.py for GET /api/public/stats only | 30s TTL (`_STATS_TTL = 30`) |
| Response compression | CompressionMiddleware | gzip when client accepts and body ≥1024 bytes |
| Connection pooling | database.py engine (prod) | DB_POOL_SIZE=10, DB_MAX_OVERFLOW=20, pool_pre_ping |
| SQLite pragmas (dev) | database.py | foreign_keys=ON, WAL journal |

There is no decorator-based application cache — the former cache layer was removed together with its features (see 06-architecture).

## Rules
1. No N+1 queries — batch-fetch related rows once, index into a dict
2. React Query: staleTime 30s, gcTime 5min; SSE events trigger targeted invalidation
3. Heavy UI components load via dynamic import
4. New expensive public reads may add an inline TTL dict following the public/stats pattern — nothing more
5. API responses >1KB ship gzipped when the client accepts gzip

## Examples
- GET /api/public/stats hits `_stats_cache` for 30s between DB aggregations
- Graph endpoint builds nodes/edges from two batched queries, not per-skill lookups

## Edge Cases
- Cold SQLite on first request → first hit slower, subsequent hits warm
- Many concurrent SSE streams consume per-user queues → bounded queues drop rather than block

## Failure Cases
- N+1 introduced → blocked in review (rule 1)
- Latency budget exceeded after a change → fix before merge

## Recovery Procedures
1. Re-run timing against the affected endpoints after any schema/index change
2. Add a missing index via DDL + entities update (verify with verify_schema.py)

## Refactoring Strategy
- Refresh benchmarks each release
- Revisit caching scope only if measured need appears; changes require an ADR
