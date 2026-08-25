# SS-EDS: Caching

## Purpose
Document the multi-layer caching strategy — Redis-backed with SQLite/in-memory fallback, decorator-based API caching, and React Query client-side cache invalidation.

## Responsibilities
- Provide `@cached` decorator for server-side function result caching
- Provide `@invalidate_cache` decorator for cache busting on mutations
- Manage Redis connection with automatic SQLite/in-memory fallback
- Configure React Query client-side cache (staleTime, gcTime)
- Handle cache invalidation on SSE-triggered data mutations

## Inputs
- API response patterns and TTL requirements
- Data mutation frequency
- Performance targets (TTFB <100ms)

## Outputs
- Cache configuration (TTL=300s, pool_size=10)
- Cache invalidation rules
- Redis → InMemory fallback chain

## Dependencies
- 07-backend (cache/cache_service.py)
- 08-frontend (React Query)
- 10-database (connection pooling)

## Sequence: Cache Read Flow
```
Service call wrapped in @cached(ttl=300)
  → Generate cache key: module:function:hash(args)
  → Try Redis GET (if connected)
  → Hit? → Return cached value
  → Miss? → Try SQLite in-memory dict
  → Hit? → Return cached value
  → Miss? → Execute function → SET result → Return
```

## Sequence: Cache Invalidation Flow
```
Mutation endpoint wrapped in @invalidate_cache("pattern:*")
  → Execute mutation (DB write)
  → Delete all keys matching pattern from Redis
  → Delete all matching keys from in-memory cache
  → Return mutation result
```

## State Diagram: Cache Entry Lifecycle
```
[Empty] → [Function Executes] → [Cached (ttl=300s)] → [Expired]
                                ↓                        ↓
                          [Cache Hit]           [Cache Miss → Recompute]
                                ↓
                    [Cache Invalidation at Mutation]
```

## Caching Layers
| Layer | Technology | Config |
|-------|------------|--------|
| Server-side API | Redis / InMemory | @cached(ttl=300) |
| Server-side busting | Redis / InMemory | @invalidate_cache(pattern) |
| Client-side (React Query) | Browser memory | staleTime=30s, gcTime=5min |
| Asset cache | Browser/CDN | next.config.js headers |

## Cache Key Format
```
{module}:{function_name}:{hash(kwargs)}:{hash(args[1:])}
Example: backend.services.analytics_service:get_dashboard:12345:67890
```

## Connection Pooling (database.py)
```python
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))        # default: 10
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))  # default: 20
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # default: 30s
pool_pre_ping=True  # verify connections before use
```

## SQLite WAL Performance (dev mode)
```python
PRAGMA foreign_keys=ON
PRAGMA journal_mode=WAL
PRAGMA synchronous=NORMAL
PRAGMA cache_size=-8000   # 8MB cache
PRAGMA temp_store=MEMORY
```

## Server-side Cache Decorators
```python
@cached(ttl=300)           # Cache result for 5 minutes
def get_dashboard(db, user):
    return compute_dashboard(db, user)

@invalidate_cache("dashboard:*")  # Bust dashboard cache on mutation
def update_profile(db, user_id, data):
    return repository.update(db, user_id, data)
```

## React Query Configuration
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,      // 30s until stale
      gcTime: 5 * 60 * 1000,     // 5min garbage collection
      retry: 2,                   // retry failed requests twice
    },
  },
});
```

## Rules
1. Cache TTL defaults to 300s (5 minutes), configurable per @cached
2. Auth queries never cached (user profile, permissions)
3. SSE events trigger targeted React Query invalidation
4. Connection pool: pool_size=10, max_overflow=20
5. Fallback chain: Redis → InMemory dict → Compute

## Edge Cases
- Redis unavailable → silent fallback to in-memory dict
- Cache stampede on expiry → mitigated by short TTL + fallback compute
- Race condition on invalidation → stale data served for at most one request

## Failure Cases
- Redis connection leak → max_overflow exhausted, queued
- In-memory cache OOM → periodic cleanup (expired keys pruned on access)
- Cache key collision → hash-based keys prevent collisions

## Recovery Procedures
1. Restart with cleared cache: delete redis keys or restart server
2. Bump CACHE_TTL env var for slower-changing data
3. Clear React Query cache: queryClient.clear()
