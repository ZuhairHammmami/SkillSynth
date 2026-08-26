# SS-EDS: State Management

## Purpose
Document the layered state management strategy: React Server Components for initial data fetching, React Query for client-side server state, Zustand for auth session only, and SSE-driven cache invalidation. No Redux, no global state libraries beyond these.

## Responsibilities
- Manage server data synchronization via React Query v5
- Maintain auth session state (isAuthenticated, isLoading) via Zustand
- Handle local UI state (forms, toggles) via React useState
- Invalidate React Query caches reactively via SSE events
- Provide optimistic updates for mutations to improve UX

## Inputs
- Backend API response shapes
- Authentication flow (JWT cookie-based)
- Real-time SSE event types for targeted invalidation

## Outputs
- Centralized query key factory (42+ keys)
- Zustand auth store (isAuthenticated, isLoading, logout)
- SSE-driven query invalidation utility
- Provider wrapper (QueryClientProvider + DevTools)

## Dependencies
- 08-frontend (React Query, Zustand integration)
- 12-realtime (SSE events trigger invalidation)
- 24-caching (staleTime, gcTime configuration)

## State Architecture
| Concern | Technology | Scope | Persistence | Staleness |
|---------|------------|-------|-------------|-----------|
| Server data | React Query v5 | Global | Memory (gcTime=5min) | staleTime=30s |
| Auth session | Zustand | Global | Memory (synced with cookie) | Instant |
| Form state | React useState | Component | None | N/A |
| UI toggles | React useState | Component | None | N/A |
| Toasts | Sonner | Global | None | Auto-dismiss |

## Sequence: Data Fetch Flow
```
Server Component (initial load) → await fetch API → render HTML immediately
Client Component (subsequent) → useQuery → cache check → stale? → refetch → UI update
SSE Event → queryInvalidator → targeted invalidateQueries → refetch → UI update
```

## Sequence: Mutation with Optimistic Update
```
User → Click Complete → useMutation → onMutate: update cache optimistically
→ POST /api/steps/complete → onSuccess: invalidate related queries
→ onError: rollback optimistic update → Sonner error toast
```

## Query Key Factory — Current Structure
```typescript
// src/shared/api/query-keys.ts
queryKeys = {
  user:     { all, current, profile },
  paths:    { all, lists, list(filters), details, detail(id), progress, progressByPath(id) },
  wizard:   { all, options, generateOptions(goal), templates, assessment },
  assessments: { all, lists, list(pathId), details, detail(id), results, resultsByPath(id) },
  analytics:   { all, dashboard, skillGrowth, learningHistory, pathProgress, pathProgressById, learningVelocity },
  ~~gamification: { all, profile },~~ /* REMOVED */
  admin: {
    all, stats,
    users: { all, list(page, pageSize), detail(id) },
    paths: { all, list(page, pageSize), detail(id) },
    resources: { all, list, detail(id) },
    skills: { all, list, detail(id) },
    categories: { all, list },
    jobRoles: { all, list },
  },
}
```

## Provider Setup
```typescript
// shared/lib/providers.tsx
QueryClient with: staleTime=30s, gcTime=5min, refetchOnWindowFocus=true, retry=2
Wraps children in QueryClientProvider + ReactQueryDevtools (dev only)
```

## Rules
1. Server state always in React Query — never in Zustand or useState
2. Zustand holds ONLY `isAuthenticated`, `isLoading`, and `logout()` — no user data
3. React Query for all API data; user profile is fetched via `['user', 'current']` query
4. SSE events trigger targeted `invalidateQueries` — never full clear
5. Mutations use optimistic updates with rollback on error
6. 30s staleTime for list queries, 0s staleTime for profile/auth queries

## Examples
- Path list: `useQuery({ queryKey: ['paths', 'list'], queryFn: fetchPaths })`
- Profile: `useQuery({ queryKey: ['user', 'current'], staleTime: 0 })` — always fresh
- Mutation: `useMutation({ mutationFn: updateSkill, onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'skills'] }) })`

## Edge Cases
- Stale data shown while background refetch happens → React Query serves cache
- Multiple mutations in flight → serialized by React Query per key
- Zustand reset on page refresh → re-synced from cookie on mount

## Failure Cases
- Zustand out of sync with cookie → brief flash of unauthenticated state
- React Query infinite refetch loop → check query key dependencies
- SSE event missed → stale data until next manual refetch

## Recovery Procedures
1. Clear React Query cache: `queryClient.clear()`
2. Reset Zustand: `useAuthStore.getState().logout()`
3. Force refetch: `queryClient.refetchQueries({ queryKey: [...] })`

## Refactoring Strategy
- Add Zustand persist middleware for user preferences (theme, locale)
- Extract query key factory into typed package
- Implement optimistic update helpers for common mutation patterns
