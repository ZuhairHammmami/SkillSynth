# SS-EDS: Frontend

## Purpose
Document the Next.js 14 App Router student frontend at `src/frontend` (:3000): bilingual ar/en RTL-first delivery, directory layout (`app/`, `shared/`, `i18n/`, `types/`), data-fetching hooks, and build pipeline.

## Responsibilities
- Render landing, auth, and student pages (13 page routes)
- Protect student routes via `middleware.ts` and client guards
- Fetch API data through typed hooks in `shared/hooks/`
- Enforce 100% i18n coverage — ar.json/en.json at 560-key parity
- Provide the shared UI kit (shadcn/ui primitives + custom components)
- Maintain the build pipeline: type-check → lint → build

## Inputs
- Backend REST contract (22-api) over Bearer JWT
- Design tokens (20-ui-system — Linear/Notion style, no gradients)
- Localization messages (13-localization)

## Outputs
- 13 page.tsx routes + error boundaries (`app/error.tsx`, `app/global-error.tsx`)
- API client with automatic Bearer injection from the `authToken` cookie
- SSE consumer hook (`shared/hooks/useSSE.ts`)

## Dependencies
- 06-architecture (system topology)
- 20-ui-system (design tokens)
- 22-api (endpoints)
- 35-state-management (React Query patterns)
- 36-component-library (shared UI)
- 13-localization (message catalogs)

## Directory Structure
```
src/frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # <html lang="ar" dir="rtl">, Tajawal font, providers
│   │   ├── page.tsx              # Landing (server component)
│   │   ├── globals.css           # HSL design tokens
│   │   ├── error.tsx / global-error.tsx   # Error boundaries
│   │   ├── (auth)/               # login · register · forgot-password · reset-password
│   │   ├── (student)/            # dashboard · learn · learn/[id] · analytics · profile · settings
│   │   ├── paths/page.tsx        # Path list/detail entry
│   │   └── wizard/page.tsx       # Path-generation wizard
│   ├── shared/
│   │   ├── api/                  # Endpoint call modules
│   │   ├── components/           # Logo, LocaleSwitcher, Loading, ...
│   │   ├── hooks/                # useAuthApi · useAssessmentApi · usePathApi ·
│   │   │                         # useAnalyticsApi · useSystemApi · useSSE
│   │   ├── lib/                  # api client (Bearer from cookie), utils, providers
│   │   └── ui/                   # shadcn/ui primitives
│   ├── i18n/                     # next-intl config, provider, messages/ar+en.json (560 keys each)
│   └── types/                    # Shared TypeScript types
├── middleware.ts                 # Locale/route handling at the edge
├── tailwind.config.js · tsconfig.json · next.config.js · package.json
```
Domain typing lives in `types/`; data access lives in `shared/api/` + `shared/hooks/` — the frontend intentionally has no additional domain-layer directories beyond these four.

## Build Pipeline
```
pnpm type-check (tsc --noEmit) → pnpm lint (next lint) → pnpm build
```
Run from `src/frontend` with pnpm only.

## Rules
1. Server components by default; `'use client'` only where hooks/events require it
2. All copy via next-intl `t()` — zero hardcoded strings; ar/en key parity is maintained
3. RTL-first: logical CSS properties (`ms-/me-`, `ps-/pe-`) everywhere
4. Auth token lives in the `authToken` cookie (not HttpOnly); api.ts attaches `Authorization: Bearer` automatically
5. SSE via EventSource in useSSE; events trigger React Query invalidation
6. No gradients/neon/glassmorphism; tokens from globals.css only

## Examples
- Login flow: `(auth)/login/page.tsx` → useAuthApi().loginMutation → POST /api/auth/token → cookie set → redirect `/dashboard`
- Live update: useSSE receives `path_generated` → invalidates path queries → UI refetches

## Edge Cases
- Missing/expired token on API call → 401 → redirect to `/login`
- Locale resolution: cookie → `Accept-Language` → default `ar`
- Render error inside a route → caught by `app/error.tsx` (global fallback: `global-error.tsx`)

## Failure Cases
- React Query cache stale after missed SSE event → user refetches on window focus
- Missing i18n key → raw key rendered; parity check keeps ar/en aligned

## Recovery Procedures
1. Clear the `authToken` cookie and reload to reset session state
2. Run `queryClient.clear()` for a full client-cache reset

## Refactoring Strategy
- Keep route groups flat; new domains add a hook file + api module, not a new top-level layer
- Extract reusable visuals into `shared/components/` before duplicating

The admin application is documented separately in 09-admin.
