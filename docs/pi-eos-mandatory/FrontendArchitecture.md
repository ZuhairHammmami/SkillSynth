# Frontend Architecture

## Stack
- **Framework**: Next.js 14 (App Router)
- **UI**: React 18, Tailwind CSS, shadcn/ui
- **State**: React Query (server data) + Zustand (auth session)
- **i18n**: next-intl (AR/EN, RTL/LTR)
- **Build**: pnpm → tsc → next build

## Route Groups
| Group | Prefix | Routes | Auth |
|-------|--------|--------|------|
| `(auth)` | `/login`, `/register`, etc. | 4 | Public (redirect if authed) |
| `(student)` | `/dashboard`, `/learn`, etc. | 7 | JWT required |
| `admin` | `/admin/*` | 11 | JWT + `is_admin=True` |

## Directory Structure (Feature-Sliced)
```
src/frontend/src/
├── app/            # App Router pages (3 route groups)
├── shared/
│   ├── ui/         # shadcn/ui primitives (21 components)
│   ├── components/ # Custom components (Logo, LocaleSwitcher, PathWizard)
│   ├── hooks/      # Custom hooks (useAuthApi, useSSE, etc.)
│   ├── lib/        # Providers, utils, API client
│   └── api/        # Query keys, API functions
├── i18n/           # next-intl config, messages (en.json, ar.json)
└── types/          # TypeScript type definitions
```

## State Management
| Layer | Technology | Scope |
|-------|-----------|-------|
| Server State | React Query | API data (paths, skills, analytics) |
| Auth Session | Zustand | Current user, token, permissions |
| Local UI | React useState | Forms, modals, wizard state |
| Real-time | SSE (useSSE hook) | Progress updates, notifications |

## Build Pipeline
```bash
pnpm type-check  # tsc --noEmit
pnpm lint        # next lint
pnpm build       # tsc + next build
```

## Key Conventions
1. Server components by default, `'use client'` only when needed
2. All user-facing text via `useTranslations('key')`
3. API client auto-injects `authToken` cookie
4. Dynamic imports for heavy components (admin charts)
