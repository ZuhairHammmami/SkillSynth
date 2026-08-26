# SkillSynth Redesign — Design Spec (2026-08-26)

**Status:** Approved. Architectural overhaul of the two front-end applications (student + admin). Backend (FastAPI) and `skillsynth` CLI/seed/test tooling are **unchanged**.

## 1. Goal & Interpretation

The user requested a "radical redesign … the exact opposite of the current versions in every respect" and that the result "must not look like it was developed by an AI model." Interpretation (confirmed with user):

- **Invert the visual language and layout paradigm** — escape the generic "clean SaaS / shadcn" aesthetic (white bg, blue primary, rounded cards, icon-rail sidebars, Tajawal) into a **Warm-Craft editorial** identity.
- **Replace the entire front-end stack** — no React/Next/Tailwind/shadcn/Radix/TanStack-Query/axios/lucide/sonner.
- **Preserve all functionality** — auth, learning engine, path CRUD, the 5-step wizard, SSE, AI gating, admin CRUD + force-delete, bilingual AR/EN + RTL, etc. Breaking product behavior is out of scope.
- Backend API contract, ports, and the `skillsynth run` launcher stay as-is (we rebuild *in place* inside `src/frontend` and `src/admin-app`).

## 2. Tech Stack (full inversion)

| Concern | Current | New (both apps) |
|---|---|---|
| Framework | Next.js 14 App Router, React 18 | **SvelteKit + Svelte 5** (runes), Vite, TypeScript |
| Styling | Tailwind + shadcn token layer | **Hand-written CSS** — CSS custom properties design tokens, component-scoped `.css`, logical properties for RTL. No utility framework. |
| Data fetching | axios + TanStack Query v5 | Native `fetch` wrapper (`$lib/api/client.ts`) + a tiny custom query store (`$lib/query`) replicating `staleTime` + key-based invalidation **preserving the exact SSE invalidation key strings** |
| Auth | js-cookie + React Context | Same cookies (`authToken` student / `adminToken` admin), Svelte stores + route guards in `+layout.svelte` / `hooks` |
| Icons | lucide-react | **Custom hand-drawn inline SVG icon set** (`$lib/icons`) |
| Toasts | sonner | Tiny custom toast store + `<Toaster>` component |
| i18n (student) | next-intl | Hand-rolled: port 595-key `en`/`ar` catalogs into `$lib/i18n`, cookie-driven locale, sets `<html lang/dir>` |
| Fonts | Tajawal | Warm-craft pairing (§4) |
| Build/run | `pnpm dev` (Next) | `pnpm dev` (Vite/SvelteKit); ports 3000 (student) / 3001 (admin) via `vite.config.ts` |

Both apps remain separate SvelteKit projects in their existing folders so `skillsynth run` continues to spawn them. Deps in `package.json` are swapped to SvelteKit (`svelte`, `@sveltejs/kit`, `@sveltejs/adapter-auto`, `vite`, `svelte-check`, `typescript`, `@sveltejs/vite-plugin-svelte`). `.env` uses `PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api`.

## 3. Visual Identity — "Warm Craft" (anti-AI)

- **Palette (CSS tokens):** paper bg `#FBF6EC`, ink text `#2A2521`, muted clay `#8A7B6C`, **accent ochre `#B5862E`**, **secondary sage `#7C8A6B`**, success/warning/destructive derived warm tones. *No blue, no pure white, no neutral gray SaaS.*
- **Type:** expressive display serif/sans — **Bricolage Grotesque** (Latin display), **El Messiri** (Arabic display), **Public Sans** (body/UI). Large editorial headlines, generous leading.
- **Surfaces:** hairline 1px borders instead of drop-shadows; tiny intentional radii (2–4px); subtle **paper-grain texture** (SVG noise data-URI); dashed dividers; small hand-drawn underline/marker accents.
- **Layout paradigm:** SaaS card-grid → **editorial "journal / worksheet"**. Sidebar becomes a warm **"contents rail"** with crafted list + tiny illustrations. Landing hero uses a **custom hand-drawn SVG illustration** (plants / paths-as-roads), not a stock gradient.
- **Motion:** minimal, hand-feel (gentle settle / stroke-draw on hero), none of the generic fade/slide defaults.
- **RTL:** all layout uses CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline`, `border-inline`); `dir` flips automatically with locale.

## 4. Structure (all features preserved, re-presented)

### Student app (`src/frontend`)
- Public: `/` landing (editorial rewrite), `/login`, `/register`, `/forgot-password`, `/reset-password`
- App shell (guarded, "contents rail"): `/dashboard`, `/learn`, `/learn/[id]`, `/profile`, `/settings`, `/analytics`, `/wizard`
- Wizard: 5-step state machine (Goal → Preferences → Assessment → Results → Summary) with AI quiz + `/wizard/analysis`; `TakeQuizDialog` practice quiz + `/ai/explain`; SSE bus; AI-503 graceful degradation.
- $lib layout: `api/` (client + domain wrappers), `query/` (cache store), `stores/` (auth, locale, sse), `i18n/`, `icons/`, `components/` (design system + domain), `types/`.

### Admin app (`src/admin-app`, English-only, "workshop/atelier" utility tone)
- `/` login; guarded shell: `/dashboard`, `/users`, `/categories`, `/skills`, `/resources`, `/job-roles`, `/assessments`, `/paths`, `/reports`, `/health`, `/settings`, `/audit-logs`, `/backups`, `/db-inspector`, `/feature-flags`
- Centralized `$lib/api`; `DeleteButton` **force-delete `409 → ?force=true`** flow preserved exactly; skill create uses `category_ids` (array) / edit uses `category_id` (single) contract preserved; AI toggle via `PUT /admin/feature-flags` preserved.
- **New:** live SSE activity ticker using `/realtime/admin/events` (backend already supported, currently missing in UI).

## 5. Functional Parity Checklist (must keep)
- Auth (login/register/forgot/reset/change-password) + route guards; JWT in `authToken`/`adminToken` cookies; `is_admin` gate.
- Path list/detail, **step complete/undo**, **delete path**, **generate path** from wizard.
- 5-step wizard two-phase SS-AI; AI-503 degrade.
- SSE to `/realtime/events` (student) and `/realtime/admin/events` (admin); cache invalidation on `path_generated` / `assessment_completed` using the preserved `compat` query keys.
- Practice quiz grading (`/assessments/submit`) + `/ai/explain` walkthrough; `proficiency_adjusted` live badge.
- Analytics endpoints (dashboard, skill-growth, learning analysis/weaknesses, velocity).
- **Bilingual AR/EN + RTL**, 595-key parity catalogs, live `LocaleSwitcher`, logical-property CSS.
- Toasts for all mutation feedback.
- Admin CRUD (users/categories/skills/resources/job-roles) + assessments/paths read + **force-delete** + change-password + reports/aggregated + system-health + backups (create/list/download) + db-inspector (poll 30s) + audit-logs + feature-flags toggle.
- Error handling surfaces.

## 6. Tooling & Verification
- Rebuild in existing folders; `package.json` swaps to SvelteKit; `.env` uses `PUBLIC_API_BASE_URL`.
- Reproduce verification: `pnpm check` (svelte-check) + `pnpm build` replace `type-check`/`lint`/`build`. Backend `skillsynth test` (199 tests) unaffected.
- Manual: `skillsynth run`, log in with seed creds (admin@skillsynth.io / Admin@123456, etc.), walk every feature.
- Docs (`docs/`, `AGENTS.md`, `README`) references to Next/React/pnpm-3000 updated to reflect SvelteKit.

## 7. Phased Implementation Plan
1. **Scaffold** both SvelteKit apps (config, deps, tokens, fonts, icon set, i18n base).
2. **Design system** (Button, Dialog, Input, Select, Badge, Toast, Table, Panel, nav rail, illustrations).
3. **Student core** (auth, guards, landing, shell, dashboard, learn, detail, profile, settings, analytics).
4. **Student wizard + quiz + SSE + AI gating.**
5. **Admin** (auth, guard, shell, all CRUD + force-delete, dashboards/reports/health/backups/db-inspector/audit/flags, SSE ticker).
6. **Polish** (illustrations, motion, responsive/RTL, a11y), remove Next artifacts, update docs/AGENTS, wire launcher.
7. **Verify** (svelte-check, build, manual walkthrough).

## 8. Risks & Mitigations
- **Scope:** large surface → parallelize feature phases via sub-agents after the shared foundation (Phase 1–2) is built and committed.
- **Svelte 5 runes vs stores:** use runes (`$state`/`$derived`/`$effect`) in components; module-level stores for cross-cutting (auth/locale/sse/query).
- **SSE invalidation parity:** keep the exact `compat` query key strings so `sseBus` invalidation matches backend event frames.
- **i18n port:** copy existing `en.json`/`ar.json` catalogs verbatim; adjust only key-access calls.
- **RTL:** rely on logical CSS properties; avoid physical `left/right`.
