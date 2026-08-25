# SS-EDS: Frontend

## Purpose
Document the Next.js 14 App Router frontend architecture, route groups, Feature-Sliced Design directory layout, RTL-first bilingual i18n, state management layers, and build pipeline.

## Responsibilities
- Render all user-facing pages across 3 route groups (auth, student, admin) + landing
- Implement route protection via client-side guards and JWT cookie validation
- Manage state via React Query (server data), Zustand (auth session), and React state (local UI)
- Enforce 100% next-intl i18n coverage — zero hardcoded strings
- Provide shared UI library (shadcn/ui primitives, custom components)
- Maintain build pipeline: type-check → lint → build

## Inputs
- Backend REST API contract (22-api)
- Design system tokens (20-ui-system)
- Component library specs (36-component-library)
- Localization message keys (13-localization)

## Outputs
- 24 routes across 3 route groups + landing page
- Shared JS bundle (234kB gzip)
- API client with auto Bearer token injection and refresh handling

## Dependencies
- 06-architecture (dual-backend pattern)
- 20-ui-system (design tokens)
- 22-api (endpoint definitions)
- 35-state-management (React Query + Zustand)
- 36-component-library (shared UI)
- 13-localization (next-intl messages)

## Directory Structure
```
src/frontend/
├── src/
│   ├── app/                     # Next.js App Router pages
│   │   ├── layout.tsx           # Root: locale detection, font loading, providers
│   │   ├── page.tsx             # Landing page (hero, features, CTA)
│   │   ├── globals.css          # HSL CSS variables, base styles, scrollbar
│   │   ├── (auth)/              # Route group — Login, Register, Forgot/Reset Password
│   │   │   ├── layout.tsx       # Auth layout (centered form, right-side illustration)
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   ├── forgot-password/page.tsx
│   │   │   └── reset-password/page.tsx
│   │   ├── (student)/            # Route group — authenticated learner pages
│   │   │   ├── layout.tsx        # Student layout (sidebar, top bar, user section)
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── learn/page.tsx
│   │   │   ├── learn/[id]/page.tsx
│   │   │   ├── analytics/page.tsx
│   │   │   ├── profile/page.tsx
│   │   │   └── settings/page.tsx
│   │   └── admin/               # Separate admin application
│   │       ├── layout.tsx        # Admin layout (sidebar, badge, switch-to-student)
│   │       ├── page.tsx          # Dashboard
│   │       ├── users/page.tsx
│   │       ├── skills/page.tsx
│   │       ├── categories/page.tsx
│   │       ├── paths/page.tsx
│   │       ├── resources/page.tsx
│   │       ├── job-roles/page.tsx
│   │       ├── audit-log/page.tsx
│   │       ├── analytics/page.tsx
│   │       └── settings/page.tsx
│   ├── shared/                  # Reusable across all route groups
│   │   ├── ui/                  # shadcn/ui primitives (21 components)
│   │   ├── components/          # Custom components (Logo, LocaleSwitcher, Loading)
│   │   ├── hooks/               # useApi, useSSE, useWebSocket, useToast, etc.
│   │   ├── lib/                 # Providers, utils, queryInvalidator, api client
│   │   ├── store/               # Zustand auth store
│   │   ├── api/                 # API client, query keys, prefetch helpers
│   │   └── services/            # Domain services (Assessment, Mastery, Path, etc.)
│   ├── entities/                # TypeScript entity definitions
│   ├── i18n/                    # next-intl config, providers, messages
│   └── types/                   # Shared TypeScript types
├── package.json                 # Dependencies and scripts
├── tailwind.config.js           # shadcn/ui theme, animations
├── tsconfig.json
└── next.config.js
```

## Build Pipeline
```
pnpm type-check (tsc --noEmit) → pnpm lint (next lint) → pnpm build (tsc + next build)
```
- Build produces optimized static + server bundles
- Shared JS chunk ~234kB, code-split per route
- Font (Tajawal) loaded via next/font with swap strategy

## Rules
1. Server components are default; mark `'use client'` only when needed (hooks, events, browser API)
2. Route groups `(auth)`, `(student)` provide isolated layouts without URL nesting
3. All text must use next-intl `t()` — zero hardcoded strings
4. pnpm is the only package manager
5. Working directory must be `src/frontend` before any command
6. Dynamic imports for heavy components (admin, analytics charts)

## Examples
- API client auto-injects Bearer from `authToken` cookie (see `shared/lib/api.ts`)
- Student layout: sidebar with nav items, user avatar, XP display, LocaleSwitcher
- Landing page: server component with no client interactivity

## Edge Cases
- Cookie missing during API call → 401 → auto-redirect to `/login`
- Locale detection: `NEXT_LOCALE` cookie → `Accept-Language` → `'en'` default
- Loading state on auth pages before session is initialized

## Failure Cases
- React Query cache stale after SSE miss → user sees outdated data
- Zustand session out of sync with cookie → flash of unauthenticated UI
- next-intl message missing → key name rendered as fallback

## Recovery Procedures
1. Clear `authToken` cookie and reload
2. Run `queryClient.clear()` for full cache reset
3. Check browser network tab for API errors

## Refactoring Strategy
- Extract shared components to external npm package
- Add Storybook for visual regression
- Incrementally migrate to React Server Components where possible
