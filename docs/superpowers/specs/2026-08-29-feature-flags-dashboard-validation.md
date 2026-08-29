# Spec — Feature Flags, Dashboard & Validation Overhaul

Project: SkillSynth. Branch-style work **in place** (no worktree — the working
tree carries a large body of pre-existing UNCOMMITTED redesign; same ruling as
prior plans on this branch). This spec is the binding authority for the plan
`2026-08-29-skillsynth-feature-flags-dashboard-validation.md`.

## 1. Goal

1. Make backend feature flags **editable and validated** (schema-driven), wire
   every flag into its runtime reader, and expose a schema endpoint + validated
   bulk PUT — while preserving the existing flat GET contract.
2. Redesign the admin **feature-flags** page: schema-driven per-type controls,
   Live / Applies-after-restart / read-only badges, and a global staged Save bar
   with per-field 422 errors.
3. Redesign the student **dashboard** page: real KPI cards, a weekly activity
   chart, a Recent Activity feed, and "Your Paths" with per-path progress.
4. Roll out **client-side validation** to both apps (learner forms + admin
   CRUD dialogs), hand-rolled (no new dependency), bilingual, mirroring the
   backend rules.

## 2. Global constraints (bind every task)

- Backend: every function ≤40 lines with a single-purpose docstring stating
  caller/callee relationships; every file <300 lines; imports via
  `from backend import X`. No schema/DDL changes (15-table invariant untouched;
  settings stay file-backed JSON, no new table).
- Frontends (SvelteKit 5, runes): i18n leaf-key parity EXACT between
  `en.json` and `ar.json` (both apps). 0 hardcoded user-visible strings.
  RTL-first: use logical properties (`inset-inline-start`,
  `margin-inline`, `text-align: start`) — no `[dir]`-specific rules unless
  unavoidable. Design tokens only (`--accent-deep`, `--line`, `--paper`,
  `--muted`, `--danger`, `--radius`, …). No neon/gradients/glassmorphism.
  No new npm dependencies (validation is hand-rolled).
- File size: any created/grown file <300 lines. Follow existing Svelte 5
  runes patterns and existing component/API-client conventions in each app.
- Scope discipline: do exactly what the task says; do not restructure
  unrelated code in touched files.
- Commit hygiene: stage ONLY the files each task names (exact paths). The
  working tree is deliberately dirty; never stage `.env*`; never commit
  unrelated files. Conventional commit messages matching repo style.
  Small pre-existing uncommitted deltas on a task's named files ride along
  inside that task's commit (documented per task in the brief).
- Backend verification: `PYTHONPATH=src python -m pytest tests/ -q`
  (isolated temp DB); tests use a temp `SETTINGS_PATH` + `_CACHE` reset.
- Frontend verification (both apps): `pnpm check` (svelte-check — 0 errors,
  0 warnings) and `pnpm build` (vite build). i18n parity: en/ar key sets
  identical.
- Plans are the authority; where a task's text conflicts with these
  constraints the constraint wins and the implementer reports the conflict.

## 3. Feature-flag schema (backend)

New file `src/backend/services/settings_schema.py`. Holds a single registry:

```python
FLAG_SCHEMA: dict[str, dict] = { key: {type, editable, live, restart, min?, max?,
    min_length?, max_length?, default, options?} ... }
```

Per-key definition (the authoritative table):

| key | type | editable | live | restart | constraints | default |
|---|---|---|---|---|---|---|
| `app_mode` | `str` | no | — | — | — | runtime `MODE` env (read-only) |
| `registration_enabled` | `bool` | yes | yes | — | — | `true` |
| `ai_enabled` | `bool` | yes | yes | — | — | env `AI_ENABLED` (default `false`) |
| `ai_path_generation` | `bool` | no | — | — | — | mirror of effective `ai_enabled` (read-only) |
| `ai_local_model` | `str` | yes | no | yes | 1..200 chars, no whitespace | env `AI_MODEL_PATH` (default `src/data/Llama-3.2-3B-Instruct-Q6_K.gguf`) |
| `real_time_updates` | `bool` | yes | yes | — | — | `true` |
| `csrf_protection` | `bool` | no | — | — | — | runtime `APP_MODE=="prod"` (read-only) |
| `rate_limiting` | `bool` | yes | yes | — | — | `true` |
| `password_policy` | `object` | yes | yes | — | `min_length` int 6..32; `require_uppercase/lowercase/digit/special_char` bools | `{min_length: 8, require_uppercase: true, require_lowercase: true, require_digit: true, require_special_char: true}` |
| `session_timeout_hours` | `int` | yes | yes | — | 1..168 | `24` |
| `account_lockout_attempts` | `int` | yes | yes | — | 1..10 | `5` |
| `lockout_minutes` | `int` | yes | yes | — | 1..1440 | `15` |
| `cors_origins` | `list[str]` | yes | no | yes | 0..20 items, each 1..200 chars, `http(s)://` scheme | env `CORS_ORIGINS` (dev list: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:3001`, `http://127.0.0.1:3001`) |

API in `settings_schema.py`:

- `get_runtime_flag(key)` → effective value: persisted settings override the
  schema default; read-only keys resolve from runtime constants/env. Used by
  runtime readers so they never reimplement merge logic.
- `build_runtime_flags()` → the 13-key flat dict for GET (contract: keys and
  value types identical to today).
- `validate_update(payload: dict)` → `(cleaned: dict, errors: dict[str, str])`.
  Errors are per-key human strings; unknown key → error for that key; wrong
  type → error; out of range → error; no silent drops.

`settings_service.py` stays a generic file-backed store. Add only:
`get_all()` (returns the raw stored dict) and `reset_cache()` (clears `_CACHE`
so a new `SETTINGS_PATH` takes effect — test isolation). No schema logic here.
Keep `get_setting`/`set_setting`/`is_ai_enabled`/`set_ai_enabled` semantics.

### Endpoints (routers/admin.py)

- `GET /api/admin/feature-flags` — stays FLAT (13 keys), now produced by
  `build_runtime_flags()`. Contract preserved.
- `GET /api/admin/feature-flags/schema` — new. Returns the FLAG_SCHEMA (the
  13-key table above, serializable: type/editable/live/restart/min/max/
  min_length/max_length/default).
- `PUT /api/admin/feature-flags` — becomes a validated **bulk map**
  `{key: value}`. `validate_update` → errors → **422** (per-key messages, no
  silent drops); else persist each editable key via `settings_service`.
  Side effects after a successful persisted set:
  - `ai_enabled` changed → preserve today's warmup-on-enable /
    reset_load_failure-on-disable behavior.
  - `rate_limiting` changed → set `limiter.enabled` accordingly (slowapi).
  - `registration_enabled`/other live keys need no extra side effects — the
    runtime readers pick them up.
  - Response: the updated runtime flag map (13-key flat shape, or at least
    the updated keys — see plan Task 3).
  - Read-only keys in the payload → 422 (not editable).

### Runtime readers (wire each live flag)

| Flag | Reader | Behavior |
|---|---|---|
| `registration_enabled` | `routers/auth.py` register handler | false → 403 with the codebase's existing detail shape |
| `account_lockout_attempts` | `services/auth_service.py` | read at check/record time (default 5) instead of module constant |
| `lockout_minutes` | `services/auth_service.py` | read at check time (default 15) |
| `session_timeout_hours` | `services/auth_service.py` | token expiry = hours×60 min, read at token-issuance time (default 24h) |
| `password_policy` | `dto/auth.py` `PasswordValidator` | validate() reads the live policy each call; defaults identical to today's literals (min_length 8, four requirements) |
| `real_time_updates` | `routers/realtime.py` + `/api/events` alias in `main.py` | false → connection stays open but events are dropped (quiet-but-open) |
| `rate_limiting` | `limiter.py` / `main.py` startup + admin PUT | `limiter.enabled` mirrors the stored flag; startup initializes it |
| `ai_enabled` | (already wired) | unchanged |

`ai_path_generation` stays a read-only display mirror of effective
`ai_enabled`. `app_mode`, `csrf_protection` stay read-only runtime values.

## 4. Admin feature-flags UI (src/admin-app)

- Fix the toggle knob RTL bug in `(app)/feature-flags/+page.svelte`: the knob
  rests at `inset-inline-start: 3px` but the checked state uses the physical
  `transform: translateX(20px)`, which is wrong-direction in RTL. Change the
  checked rule to the logical `inset-inline-start: 23px` (knob 18px in a 44px
  track: 3px rest → 23px checked gives a 3px gap on both ends) and set the
  knob transition to `transition: inset-inline-start 0.15s`. No `[dir]` rule.
- Page becomes schema-driven: fetch `GET /admin/feature-flags` +
  `GET /admin/feature-flags/schema`. Render per-type controls from the schema:
  - `bool` → toggle switch
  - `int` → number input with min/max + `inputmode="numeric"`
  - `str` → text input with min/max length + pattern (before Restart badge)
  - `list[str]` → textarea (one URL per line) for `cors_origins`
  - `object` → nested group for `password_policy` (min_length number + 4
    requirement toggles)
- Badges per flag: Live (green), "Applies after restart" (amber), Read-only
  (neutral) — from schema `live`/`restart`/`editable`.
- Global Save bar: dirty state; one validated bulk `PUT {key: value}`;
  per-field errors rendered inline from 422 detail (reuse existing
  `fieldErrorsFrom`); rollback on failure. `ai_enabled` no longer saves
  immediately on toggle.
- Extract `FlagRow.svelte` + `FlagControl.svelte` under
  `src/lib/components/`; the page stays <300 lines.
- i18n: `admin.flags.*` extension + `validation.*` (admin) in BOTH
  `en.json` / `ar.json`, key sets identical.
- Verify: `pnpm check` + `pnpm build`; manual smoke EN + AR.

## 5. Student dashboard redesign (src/frontend)

`(app)/dashboard/+page.svelte` rewritten (<300 lines). Data (parallel
Promise.all): `GET /analytics/dashboard`, `GET /analytics/learning-history`,
`GET /paths/`. **Drop `GET /progress/dashboard`** (its per-path payload is
superseded; the page currently misreads `completion_rate`/`learning_hours`/
`paths_count`/`recent_activity` off it — those live on `/analytics/dashboard`).

Blocks:
1. **KPI row** — StatCard.svelte (new): completion % (from analytics
   `completion_rate`), learning hours (real `learning_hours` value) with a
   completed/remaining steps hint computed from the already-fetched `/paths/`
   list (`Path.steps[].is_completed` summed), mastered skills
   (`mastered_skills`), learning velocity (`learning_velocity`).
2. **This-week activity** — reuse the existing
   `ActivityBarChart.svelte` (do NOT create a second chart) fed by
   `/analytics/learning-history` `daily_activity`.
3. **Recent Activity feed** — RecentActivity.svelte (new) from
   `/analytics/dashboard` `recent_activity` ("Completed <step> in <path>" +
   relative date, bilingual, empty state). If `recent_activity` items lack a
   human text, compose from their fields via i18n.
4. **Your Paths** — PathCard per path from `/paths/`, progress meter from
   `/analytics/dashboard` `path_progress` matched by path id (fall back to
   `Path.progress`), plus a "View analytics" CTA.
- Keep the `sse:path_generated` listener → invalidate + reload.
- i18n: extend `dashboardPage.*` in BOTH locales as needed; fix `stepsOf`
  (currently `"/"` in both files) to a real "x of y" format; delete the dead
  `dashboard.*` block (24 keys, verified 0 usages) from BOTH files.
- Verify: `pnpm check` + `pnpm build`; smoke EN + AR (non-zero hours, chart
  bars, RTL no-overflow).

## 6. Client-side validation (hand-rolled, both apps)

No validation library. New `validators.ts` in each app under `src/lib/validation/`
mirroring the backend rules. Shared rule table:

| Field | Rule |
|---|---|
| email | non-empty, `^[^@\s]+@[^@\s]+\.[^@\s]+$` (simple), ≤200 |
| name/fullName | 1..100 chars, forbids `<>"'\\` |
| password policy | lives in validation config: `{min_length, require_uppercase, require_lowercase, require_digit, require_special_char}` — learner app uses the DEFAULT policy constants; admin register/lockout forms use the same |
| password min/max | 6..32 (policy min_length configurable) |
| title | length 100 |
| description / long text | ≤2000 |
| weekly hours | 1..80 |
| difficulty / rating | 0..5 |
| passing score | 0..100 |
| duration | ≥0 |
| URL | must parse as `http(s)://` |
| color | hex `#` + 6 hex digits |
| options (assessment questions) | ≥2 options |
| numeric ids | positive integer |

Layout per form: hint under each field, live inline error via the existing
`error` prop (`role="alert"`), submit blocked while invalid. i18n:
`validation.*` group extended in en/ar for each app (parity exact).

Learner forms (frontend): register, login, forgot-password, reset-password,
change-password + profile (in `profile/+page.svelte`), wizard (weekly-hours
range + hint, role-search hint; levels already ranged).

Admin forms (admin-app): login (root page) + CRUD dialogs (users, skills,
categories, job-roles, resources, assessments, assessment-questions dialog).

## 7. Risk register

- password_policy tightening can lock real users out → range-gated 6..32;
  UI warning on the password_policy control; seeded creds remain valid at the
  icanon default policy.
- `ai_local_model` change needs a restart → "Applies after restart" badge,
  not applied at runtime.
- `cors_origins` is middleware-config at startup → editable but flagged
  "Applies after restart".
- Feature-flag smoke tests must restore `ai_enabled` (and any flag they flip)
  afterward — never leave `src/data/settings.json` mutated.
- Dev DB never touched (tests use temp DB + temp settings path).

## 8. Verification (final)

- `PYTHONPATH=src python -m pytest tests/ -q` (full suite green)
- `pnpm check` + `pnpm build` in `src/frontend` and `src/admin-app`
- i18n parity (en/ar key sets identical) in both apps
- Live EN + AR smoke: dashboard, feature-flags save flow, 3 validation forms
- `git diff` staging audit; feature-flag state restored after smoke