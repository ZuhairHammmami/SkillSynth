# SS-EDS: Caching

## Purpose
Document the caching reality of SkillSynth: one server-side inline TTL cache (GET /api/public/stats, 30s), gzip response compression, HTTP-level asset caching, and the React Query client cache. No decorator-based or Redis application cache exists — that layer was removed.

## Responsibilities
- Serve public stats from the in-process `_stats_cache` dict with a 30s TTL
- Compress JSON responses ≥1KB via CompressionMiddleware
- Define React Query defaults (staleTime/gcTime) and invalidation triggers
- Keep pooled DB connections healthy (pool_pre_ping) instead of caching query results

## Inputs
- Request frequency for public stats
- SSE events signaling data mutations

## Outputs
- Fast repeated reads of GET /api/public/stats (one aggregation per 30s window)
- gzipped responses for capable clients

## Dependencies
- 07-backend (main.py inline cache, middlewares/compression.py)
- 08-frontend (React Query provider)
- 10-database (connection pooling)

## Sequence: Public Stats Cache Flow
```
GET /api/public/stats
  → lock _stats_cache
  → fresh (age ≤ 30s)? → return cached value
  → stale/empty?       → run aggregations → store {value, ts} → return
```

## State Diagram: Cache Entry Lifecycle
```
[Empty] → [First request computes + stores] → [Hits for 30s] → [Expired]
                  ↑                                            ↓
                  └────────── next request recomputes ─────────┘
```

## Caching Layers (current)
| Layer | Technology | Config |
|-------|------------|--------|
| Server inline | dict in main.py (`_stats_cache`, `_STATS_TTL = 30`) | GET /api/public/stats only |
| Response compression | CompressionMiddleware | gzip when Accept-Encoding allows and body ≥1024B |
| Client queries | React Query | staleTime 30s · gcTime 5min · retry 2 |
| Static assets | Next.js build pipeline | content-hashed filenames |

Removed (do not reintroduce without an ADR): decorator-based function-result caching, its invalidation decorators, and their backing services — deleted with the features they served; docs/06-architecture lists cache/ among removed layers.

## Invalidation Model
- Server side: the stats entry simply expires after 30s; no busting API exists
- Client side: mutations invalidate query keys in their hooks' onSuccess; SSE frames (`path_generated`, `assessment_completed`) trigger targeted refetches via useSSE

## Connection Pooling (database.py, prod)
```python
create_engine(DATABASE_URL,
    pool_size=DB_POOL_SIZE,          # default 10
    max_overflow=DB_MAX_OVERFLOW,    # default 20
    pool_timeout=DB_POOL_TIMEOUT,    # default 30s
    pool_pre_ping=True)
```

## Rules
1. The inline-cache pattern is reserved for cheap-to-stale public reads; auth and per-user data are never cached server-side
2. React Query is the only client cache; do not add ad-hoc memoization layers for API data
3. Any new server cache requires an ADR (the previous layer was removed deliberately)
4. Compression skips responses that already carry Content-Encoding or are <1KB

## Examples
- Landing page polls /api/public/stats → at most one DB aggregation per 30s across all visitors
- Step completion → mutation hook invalidates ['progress'] keys → dashboard refetches

## Edge Cases
- Cache stampede is bounded by the single lock around recompute
- Redis absence has no effect — nothing depends on it (only prod rate-limit storage optionally uses it)

## Failure Cases
- Stale stats up to 30s — accepted by design for a public counter
- Memory growth of the one-entry dict is impossible (single key)

## Recovery Procedures
1. Restart clears the in-memory stats cache automatically
2. Clear client state with `queryClient.clear()` when debugging UI staleness
