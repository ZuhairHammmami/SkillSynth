# Frontend — DEPRECATED (absorbed into SS-EDS docs/08-frontend/) — Next.js

## Structure

```
src/frontend/
├── middleware.ts                    # Edge middleware — route protection, locale detection
├── next.config.js                  # Image optimization, webpack chunks, caching
├── tailwind.config.js              # Dark theme, custom colors/animations/shadows
├── tsconfig.json                   # Strict, @/* → ./src/*, @/services/* → ../services/*
├── components.json                 # shadcn/ui config (new-york style)
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root: lang=ar, dir=rtl, RootProvider + Providers
│   │   ├── page.tsx                # Landing page (hero, features, how-it-works, CTA)
│   │   ├── globals.css             # Dark theme CSS variables, custom utilities
│   │   ├── (auth)/                 # Login, Register, Forgot/Reset Password
│   │   ├── dashboard/              # Main learner dashboard
│   │   ├── paths/                  # Paths list + [id] detail (with SSE realtime)
│   │   ├── wizard/                 # 4-step path creation wizard
│   │   ├── ~~mastery-path/~~           # ~~DAG visualization (mock data)~~ **REMOVED**
│   │   ├── learn/[conceptId]/      # Concept learning room (mock data)
│   │   ├── profile/                # User profile (4 tabs)
│   │   ├── analytics/              # Learning analytics
│   │   ├── admin/                  # 15 admin pages (CRUD, reports, health, settings)
│   │   ├── api/                    # 8 Next.js API route handlers (mostly stubbed)
│   │   ├── sections/               # Landing page sections
│   │   └── components/             # ErrorBoundary variants, analytics components
│   ├── shared/
│   │   ├── components/             # AppLayout, DashboardShell, Header, PathCard, StepItem, etc.
│   │   ├── ui/                     # 22 shadcn/ui primitives
│   │   ├── hooks/                  # useConflictDetection, useMasteryPath, useNodeCompletion
│   │   ├── store/                  # Zustand authStore (isAuthenticated, isLoading)
│   │   ├── lib/                    # api.ts (Axios), utils.ts (cn), providers.tsx (React Query)
│   │   ├── api/                    # Query keys factory
│   │   └── services/               # ConflictNotificationService (stub), AssessmentService
│   ├── features/
│   │   ├── auth/components/        # AuthGuard, AdminGuard, LoginForm, RegisterForm
│   │   ├── auth/hooks/             # useLogin, useRegister, useLogout, useForgotPassword, useResetPassword
│   │   ├── user/hooks/             # useUser, useChangePassword, useUpdateProfile
│   │   ├── wizard/components/      # 4 wizard steps
│   │   ├── paths/hooks/            # usePaths, usePathDetails, useDeletePath, useGeneratePath
│   │   ├── admin/components/       # AdminSidebar, AdminHeader, UsersTable
│   │   └── analytics/              # Chart/analytics components
│   ├── i18n/                       # next-intl config, provider, en.json (908 lines), ar.json (831 lines)
│   ├── lib/                        # supabase.ts (browser client, unused in auth flow)
│   ├── entities/                   # KnowledgeNode.ts, UserPath.ts (frontend copies)
│   └── types/                      # supabase.ts (Database type for 4 tables)
```

## Route Protection (Two Layers)

### Layer 1: Edge Middleware (`middleware.ts`)
- Matches: `/dashboard`, `/wizard`, `/paths`, `/profile`, ~~`/mastery-path`,~~ `/learn`, `/admin`, `/login`, `/register`, `/forgot-password`, `/reset-password`
- Checks `authToken` cookie → redirects to `/login?redirect=<path>` if missing on protected routes
- Redirects authenticated users away from auth routes → `/dashboard`
- Supports `adminSwitchToUser` cookie
- Sets `NEXT_LOCALE` cookie from `Accept-Language` if missing

### Layer 2: Client Guards
- **`AuthGuard`** — Reads Zustand `isAuthenticated`, skeleton while loading, redirect to `/login`
- **`AdminGuard`** — Checks `is_admin` from `useUser()`, redirect to `/dashboard` if not admin

## State Management

| Concern | Technology | Details |
|---------|------------|---------|
| Server data | React Query v5 | 30s staleTime, 5min gcTime, retry 2 |
| Auth session | Zustand | `isAuthenticated`, `isLoading` — synced from `useUser()` |
| Client state | React useState | Wizard step/form (localStorage persisted), UI toggles |
| Toasts | Sonner | `toast.success/error/info` |

**Query key factory**: `src/shared/api/query-keys.ts` — centralized, type-safe keys by domain.

## i18n & RTL

- **Default**: `<html lang="ar" dir="rtl">` — Arabic-first
- **Library**: `next-intl` v3
- **Locale detection**: Cookie → `Accept-Language` → `en` default
- **Locales**: `['en', 'ar']`
- **CSS**: Uses logical properties (`ms-`/`me-`, `ps-`/`pe-`, `border-s-`/`border-e-`) + `rtl-flip` utility
- **No LTR toggle** exists despite RTL-default

## API Client (`api.ts`)

```typescript
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,  // http://127.0.0.1:8000
});
// Request interceptor: reads authToken cookie, sets Authorization: Bearer
```

## UI Framework

- **Tailwind**: Dark-only (`darkMode: ["class"]`, bg: `240 10% 3.9%`), custom glass/premium utilities
- **shadcn/ui**: New York style, 22 components, CSS variables
- **Animations**: Framer Motion (page transitions, cards, step items, DAG)
- **Icons**: Lucide React

## Next.js API Routes (8 handlers — mostly stubbed)

| Route | Status |
|-------|--------|
| `POST /api/ingest` | Mock — returns fake concept ID |
| `POST /api/mastery/explain` | **Semi-real** — Ollama→OpenAI→fallback (LLM works, DB stubs) |
| `POST /api/mastery/progress` | Mock — only logs to console |
| `GET /api/mastery/user-path` | Mock — returns null |
| `GET /api/mastery/assessment/generate` | Uses `AssessmentService` (real service) |
| `POST /api/mastery/assessment/submit` | Mock grading (simulates 60%) |
| `POST /api/projects/submit` | Mock — returns fake submission |
| `GET /api/search/discover` | Mock — hardcoded fallback results |

All have TODO comments for actual Supabase/backend integration.

## Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `AppLayout` | `shared/components/` | Route-aware layout (auth bare / learner shell / admin bare / public) |
| `DashboardShell` | `shared/components/` | Sidebar + top bar + mobile bottom nav |
| `PathCard` | `shared/components/` | Learning path card with progress, skills, hover prefetch |
| `StepItem` | `shared/components/` | Accordion step with complete/undo, resources, video embed |
| `StepProgressTracker` | `shared/components/` | Horizontal timeline with animated percentage |
| `EmptyState` | `shared/components/` | Generic empty state with actions |
| `SkeletonLoading` | `shared/components/` | 8 skeleton variants |
| `ErrorBoundary` | `app/components/` | 3 variants (generic, analytics, DAG) |
