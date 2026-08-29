# SkillSynth: Dashboard, Feature Flags & Validation Overhaul

Plan file. Spec (binding authority): `docs/superpowers/specs/2026-08-29-feature-flags-dashboard-validation.md`.

Branch-style: **work in place, NO worktree** — the working tree carries a large
body of pre-existing UNCOMMITTED redesign that these tasks build on (same
ruling as prior plans on this branch). BASE will be recorded per task at
dispatch (`git rev-parse HEAD`); the tree also contains uncommitted files this
plan itself owns (`src/backend/services/settings_service.py`,
`src/backend/services/question_bank.py`, admin/feature-flags page, student
dashboard page) — staging a task's named files commits their pre-existing
delta too; reviewers are told the factual pre-existing state.

Dependency order: A → B; C then D (sequentially — they share the student
`messages/{en,ar}.json` files); E parallelable only after D completes its
i18n block (shares nothing else) OR after C (it is a different app). F last.
Phase F does the whole-branch review.

## Global Constraints

1. Backend files: every function ≤40 lines with a single-purpose docstring
   (state its caller/callee relationships); every file <300 lines; imports
   via `from backend import X`; no schema/DDL/seed changes (15-table
   invariant; settings remain file-backed JSON, no new table).
2. Frontends are SvelteKit 5 + Svelte 5 runes (AGENTS.md's "Next.js" is
   stale). Follow existing runes patterns, existing api client + query cache,
   and existing ui components. No new npm dependencies. Validation hand-rolled.
3. i18n: in BOTH apps, every user-visible string is an i18n key from
   `src/{frontend,admin-app}/src/lib/i18n/messages/{en,ar}.json`; en/ar key
   sets must remain IDENTICAL (no parity tool exists — maintain by hand);
   0 hardcoded strings. Reuse existing keys where sensible.
4. Design system: Linear/Notion/Stripe; no neon/gradients/glassmorphism;
   existing tokens only. RTL-first — logical properties; no `[dir]`-specific
   rules unless unavoidable. Layout must not break under `dir=rtl`.
5. File size: any file created or grown stays < 300 lines.
   `src/frontend/src/routes/(app)/dashboard/+page.svelte` and
   `src/admin-app/src/routes/(app)/feature-flags/+page.svelte` stay < 300 lines.
6. Scope discipline: do exactly what the task says; do not restructure or
   "improve" unrelated code in touched files.
7. Commit hygiene: stage ONLY the exact files each task names. Working tree
   is deliberately dirty with unrelated in-progress work — NEVER stage or
   commit anything outside the task's file list, NEVER stage `.env*`. Commit
   per file-scoped change with a conventional message (`feat:`/`fix:`/
   `chore:`/`refactor:`), matching repo style.
8. Backend verify: `PYTHONPATH=src python -m pytest tests/ -q` from repo root
   (isolated temp DB + temp `SETTINGS_PATH` + `_CACHE` reset in tests).
9. Frontend verify (both apps, from each app dir):
   `pnpm check` (svelte-check: 0 errors 0 warnings) and `pnpm build`
   (vite build). Note: there is NO `type-check` script in either app; use
   `pnpm check`. i18n parity assertion: en/ar key sets identical.
10. Feature-flag smoke: any flag flipped during a test/smoke MUST be restored
    (never leave `src/data/settings.json` mutated).
11. Plans are the authority; if a task's text conflicts with these
    constraints, the constraint wins and the implementer reports the conflict.

---

## Phase A — Backend: editable/validated feature flags

### Task 1: Create `src/backend/services/settings_schema.py` — the FLAG_SCHEMA registry + validation

New file `src/backend/services/settings_schema.py` (<300 lines). Imports via
`from backend import ...`. It is the single source of truth for the 13 flags
and the ONLY module that knows them; `settings_service.py` (Task 2) stays
generic. Module constants (do not import schema logic into settings_service):

- `FLAG_SCHEMA: dict[str, dict]` — per-key metadata {type, editable, live,
  restart, min?, max?, min_length?, max_length?, default}. Use EXACTLY the
  per-key table from Spec §3 (all 13 keys; `app_mode`, `ai_path_generation`,
  `csrf_protection` → `editable:false`; `ai_local_model` + `cors_origins` →
  `editable:true, live:false, restart:true`; everything else editable+live).
  Types: `str`, `bool`, `int`, `object` (password_policy), `list[str]`
  (cors_origins).
- `get_runtime_flag(key)` — effective value: for editable keys, persisted
  settings override the schema default; for read-only keys, resolve the
  runtime value (MODE / APP_MODE=="prod" / AI_MODEL_PATH / CORS_ORIGINS env
  via `config.app_settings`; `ai_path_generation` → mirror of the effective
  `ai_enabled`). Used by runtime readers so merge logic lives only here.
- `build_runtime_flags()` → the 13-key flat dict for GET (same keys/types
  as today's handler).
- `validate_update(payload: dict)` → `(cleaned: dict, errors: dict[str, str])`:
  - unknown key → error for that key ("Unknown flag '<key>'");
  - read-only key in payload → error ("Flag '<key>' is read-only");
  - wrong JSON type (bool vs int/str; object/list shape) → error;
  - out-of-range `int` (min/max) → error;
  - `password_policy` → must contain `min_length` (int 6..32) and the four
    `require_*` bools; missing keys keep current stored/default values (only
    provided keys update) — return cleaned = payload with validation-passed
    keys (all keys validated; any error → errors populated, cleaned may be
    partial but PUT only persists when errors is empty);
  - `cors_origins` → list of strings, 0..20 items, each 1..200 chars, must
    start `http://` or `https://` → else error;
  - `str` keys (`ai_local_model`) → 1..200 chars, no internal whitespace.
  Errors are plain English message strings (frontend never surfaces them
  verbatim to end users in production but they must be precise).

Docstrings on every function. Write the file. Do NOT touch any other file.

Acceptance: file exists and imports cleanly (`python -c "from backend.services import settings_schema"` with PYTHONPATH=src); `build_runtime_flags()`
returns exactly the 13 keys with the table's value types; `validate_update`
correctly: accepts a valid bulk payload, rejects unknown key,
rejects read-only key, rejects out-of-range int, rejects bad URL scheme.
(Add a throwaway check via `python -c` — no permanent test file in this task.)

### Task 2: Extend `settings_service.py` — `get_all()` + `reset_cache()`

Edit `src/backend/services/settings_service.py` (<300 lines; currently 90).
Keep the existing generic store semantics (atomic write, lazy `_load`,
`get_setting`, `set_setting`, `is_ai_enabled`, `set_ai_enabled`, `_CACHE`,
`_LOCK`, `SETTINGS_PATH`) — do NOT add schema logic. Add:

- `get_all() -> dict` — return the raw stored settings dict (seeding via
  `_load` first). Single-purpose docstring.
- `reset_cache() -> None` — clear `_CACHE` (so a changed `SETTINGS_PATH`
  takes effect; test isolation). Single-purpose docstring.

That is the whole change. Commit message: `chore: add get_all/reset_cache to settings_service`.

Acceptance: `tests/test_settings.py` still passes (run
`PYTHONPATH=src python -m pytest tests/test_settings.py -q`); file < 300 lines.

### Task 3: Rewire `routers/admin.py` feature-flag endpoints (flat GET, schema GET, validated bulk PUT)

Edit `src/backend/routers/admin.py` (<300 lines). Keep the router-level
`require_admin` dependency. Use `settings_schema.build_runtime_flags()`,
`get_runtime_flag`, `validate_update` and `settings_service.set_setting`.

1. `GET /api/admin/feature-flags` — keep path + flat 13-key shape; body now
   produced by `build_runtime_flags()`. Contract preserved (rediscovered:
   `test_admin.py` asserts a subset of the 13 keys — that still passes).
2. NEW `GET /api/admin/feature-flags/schema` — return the serializable
   FLAG_SCHEMA (the 13-key metadata table; no functions/nested objects —
   plain JSON: `{key: {type, editable, live, restart, min?, max?,
   min_length?, max_length?, default}}`).
3. `PUT /api/admin/feature-flags` — accept a bulk map `dict[str, Any]`
   (replace the `FeatureFlagsUpdate` bool-only model — it only carried
   `ai_enabled`; drop it). Run `validate_update(payload)`:
   - errors non-empty → raise **422** detailing per-key messages (follow the
     codebase's existing error shape for 422 detail — check how other 422s
     and the error_mapping helper render; keep that contract so the frontend
     `fieldErrorsFrom` can map it).
   - errors empty → `for key, value in cleaned: settings_service.set_setting(key, value)`.
   Side effects after persist:
   - if `ai_enabled` changed → preserve warmup-on-true /
     reset_load_failure-on-false (existing behavior).
   - if `rate_limiting` changed → set `limiter.enabled = bool(value)`.
   Response: the updated runtime flag map (`build_runtime_flags()`), i.e.
   the full flat 13-key shape, so the page can sync with one DTO.
   (If import of `limiter` would create a circular import, import it lazily
   inside the handler — verify with the repo's import graph.)
4. Remove now-unused imports (e.g. the old `FeatureFlagsUpdate` BaseModel).

Commit message: `feat: schema endpoint + validated bulk PUT for feature flags`.

Acceptance: `PYTHONPATH=src python -m pytest tests/test_settings.py tests/test_admin.py -q` green (update any expectations that the old PUT response shape breaks — see Task 5 for test additions; existing tests should pass unchanged unless the old response shape regressed).

### Task 4: Wire runtime readers — register gate, lockout/expiry, password policy, SSE quiet-but-open, limiter startup

Edit these files (<300 lines each), respecting existing conventions:

1. `src/backend/routers/auth.py` — `register` handler: check
   `settings_schema.get_runtime_flag("registration_enabled")`; when false →
   403 with the codebase's existing 403 detail shape (match sibling 403s).
2. `src/backend/services/auth_service.py` — replace the module constants in
   the lockout path: `MAX_LOGIN_ATTEMPTS` reads
   `get_runtime_flag("account_lockout_attempts")` and
   `LOGIN_LOCKOUT_MINUTES` reads `get_runtime_flag("lockout_minutes")` at
   check/record time (defaults 5 / 15 preserved). Token expiry: read
   `session_timeout_hours` (default 24) × 60 at token-issuance time — do not
   keep it a module-level constant baked at import (the expiry must move
   with the flag). Keep the two existing duplicate constants in sync by
   default (admin GET already reads the runtime flag, so only auth_service's
   own path matters).
3. `src/backend/dto/auth.py` — `PasswordValidator.validate` and any
   password checks: read the live `password_policy` via
   `get_runtime_flag("password_policy")` each call (min_length default 8,
   the four require_* defaults true — identical behavior to today's
   literals when unset). Keep the common-pattern and whitespace checks.
4. SSE quiet-but-open — `src/backend/routers/realtime.py` and the
   `/api/events` alias in `src/backend/main.py`: when
   `get_runtime_flag("real_time_updates")` is false, the SSE connection
   still opens and stays alive (no error), but events are NOT delivered
   (drop at the publisher/broadcast seam — find the publisher and route the
   drop there, keeping the response-stream open with keep-alive comments if
   that is the existing pattern).
5. `src/backend/main.py` startup lifecycle — initialize the slowapi
   `limiter.enabled = bool(get_runtime_flag("rate_limiting"))` at startup so
   a restart preserves the stored value (today tests set it false directly).

Verify each reader against a runtime flag flip with a disposable
`python -c` or a one-off pytest in the shell (no permanent new test in this
task — Task 5 owns tests). Fix whatever breaks.

Commit message: `feat: wire live feature-flag readers (register/lockout/expiry/password/SSE/limiter)`.

### Task 5: Backend tests — schema, bulk PUT, and live-flag behavior

Update/extend `tests/test_settings.py` and `tests/test_admin.py` (both under
300 lines). All tests MUST use a temp `SETTINGS_PATH`
(`monkeypatch.setattr(settings_service, "SETTINGS_PATH", str(tmp_path/"settings.json"))`)
and reset `settings_service._CACHE` (per-test or autouse) — never touch the
real `src/data/settings.json`; always restore any flag state flipped inside
the test body so a failure cannot leak a mutated real file. New coverage:

- `GET /api/admin/feature-flags/schema` → 200; 13 keys; each entry has
  type/editable/live/default; read-only keys flagged.
- Schema 422s: PUT `{"unknown_key": 1}` → 422; PUT a read-only key
  (`app_mode`, `ai_path_generation`, `csrf_protection`) → 422; PUT wrong
  type (bool where int) → 422; PUT `session_timeout_hours: 1000` (out of
  range) → 422; PUT `cors_origins: ["ftp://x"]` → 422.
- Bulk PUT happy path: `{"registration_enabled": false,
  "session_timeout_hours": 12, "account_lockout_attempts": 3,
  "lockout_minutes": 5}` → 200, and `GET /feature-flags` reflects them;
  `settings_service.get_all()` has them.
- Registration 403: PUT `registration_enabled: false` → `POST
  /api/auth/register` → 403; restore true.
- Live password policy: set `password_policy.min_length: 9` → a password of
  length 8 with the 4 requirements rejects (PasswordValidator raises); restore.
- Limiter flip: PUT `rate_limiting: false` → `limiter.enabled is False`;
  PUT true → restored.
- Lockout/expiry from settings: set `account_lockout_attempts: 3` →
  three bad logins then fourth correct login blocked; set `session_timeout_hours`
  to a small value and assert the issued token's expiry math (e.g. decode
  exp) is hours×60 minutes away — or, if decoding is awkward, assert the
  auth_service function computing expiry honors the flag (choose the
  deterministic one).
- PasswordValidator lives off settings: direct unit test (no HTTP) using a
  temp settings path + policy override.

Run `PYTHONPATH=src python -m pytest tests/ -q` — the WHOLE suite must stay
green (other suites monkeypatch `settings_service.is_ai_enabled`; your
changes to settings_service/auth default reads must not break them).

Commit message: `test: feature-flag schema, bulk PUT, and live-flag behavior`.

→ Phase A commit cluster complete: **backend feature-flag capability**.

---

## Phase B — Admin app: feature-flags page redesign + RTL fix

### Task 6: Fix the toggle-knob RTL bug

File: `src/admin-app/src/routes/(app)/feature-flags/+page.svelte`. The
`.switch input:checked + .track::before` rule uses physical
`transform: translateX(20px)` (wrong direction in `dir=rtl`). Change to
logical `inset-inline-start: 23px` and set the knob transition to
`inset-inline-start 0.15s` (rest state is already `inset-inline-start: 3px`).
No `[dir]`-specific rule. Do not change anything else in this file (Task 7
rewrites it).

Acceptance (visual, on your own instinct): knob sits flush inside the track
in both LTR and RTL, animates to the inline-end side when checked.

Commit message: `fix: toggle knob RTL direction (logical inset-inline-start)`.

### Task 7: Schema-driven feature-flags page

Rewrite `src/admin-app/src/routes/(app)/feature-flags/+page.svelte` (<300
lines). Fetch both `GET /admin/feature-flags` and the NEW
`GET /admin/feature-flags/schema` (via `$lib/query` keys `['FLAGS']` /
`['FLAG_SCHEMA']`). Render per-type controls driven by the schema:

- `bool` → toggle switch
- `int` → number input (`inputmode="numeric"`, `min`/`max` from schema)
- `str` → text input (`maxlength`) + pattern for `ai_local_model`
- `list[str]` → textarea (one URL per line) for `cors_origins`
- `object` → nested `password_policy` group (min_length number + 4
  requirement toggles)
- `editable:false` → value shown read-only (no control, badge)

Per-flag badge from schema metadata: `live:true` → "Live" (ok tone) ·
`restart:true` → "Applies after restart" (warn tone) · `!editable` →
"Read-only" (neutral tone). Global **Save bar**: staged dirty state
(a dirty flag set vs last-fetched values), one validated bulk
`PUT /admin/feature-flags {key: value, ...}` on Save, per-field inline
errors from 422 via the existing `fieldErrorsFrom` (rollback inputs on
failure), Discard button, "unsaved changes" hint while dirty, Save disabled
when clean. `ai_enabled` no longer saves immediately on toggle.

i18n (also Task 9): new `admin.flags.*` keys in BOTH en/ar (save, discard,
unsavedChanges, live, appliesAfterRestart, readOnlyBadge, per-type labels,
passwordPolicy group labels, validation strings). 0 hardcoded strings.

Acceptance: `pnpm check` 0/0 in `src/admin-app`; `pnpm build` clean; save
flow works against the real backend (smoke: change a scalar, save, revert).

### Task 8: Extract FlagRow + FlagControl components

New components in `src/admin-app/src/lib/components/`:
`FlagRow.svelte` (row shell: label, badge, description, control slot, error)
and `FlagControl.svelte` (control per type, dispatches/stores value). Refactor
the Task 7 page to use them. Each < 300 lines. Commit with Task 7's UI (same
feature) or as its own chore commit — your call, but the page must stay < 300
lines.

Acceptance: `pnpm check` 0/0; page renders identically after refactor.

### Task 9: Admin i18n en/ar parity

Edit `src/admin-app/src/lib/i18n/messages/en.json` and `ar.json`: add the
`admin.flags.*` group additions + `validation.*` group used by the redesign
(and the `admin.validation.*` group Phase E will reuse for dialogs — add at
least the shared rule strings now: required, minMax, minLen, maxLen, url,
invalidEmail, hexColor, minOptions; templates/params where needed). Keep en/ar
key sets IDENTICAL (no parity tool — maintain by hand; both files already
hold 806 leaf keys, match that discipline). Do the keys from Tasks 6-8 if not
done there.

Acceptance: a parity check script (inline `node -e` or python) comparing
flattened key sets of en.json vs ar.json reports NO differences; `pnpm check`
0/0.

→ Phase B complete: **admin feature-flags UI** (verify pnpm check/build;
smoke EN + AR: knob position in RTL, save flow, badges, 422 display).

---

## Phase C — Student dashboard redesign

### Task 10: Rewrite `(app)/dashboard/+page.svelte`

File: `src/frontend/src/routes/(app)/dashboard/+page.svelte` (<300 lines;
currently 113). Replace the three fetches: DROP `GET /progress/dashboard`;
fetch in parallel (Promise.all) `GET /analytics/dashboard`,
`GET /analytics/learning-history`, `GET /paths/`. Keep the `sse:path_generated`
listener → invalidate `['analyticsDashboard']`, `['paths']`,
`['learningHistory']` (whatever $lib/query keys you use) + reload. Build:

1. **KPI row** — 4 StatCards (Task 11): completion % (`completion_rate`),
   learning hours (real `learning_hours`) + a "completed/remaining steps"
   hint computed by summing `Path.steps[].is_completed` across the fetched
   `/paths/` list (steps total = Σ steps; completed = Σ is_completed),
   mastered skills (`mastered_skills`), velocity (`learning_velocity`).
   Each with units label + compact icon. Empty/default states when the value
   is absent (i18n).
2. **This-week** — reuse the EXISTING `ActivityBarChart.svelte`
   (`src/lib/components/ActivityBarChart.svelte`) fed by
   `/analytics/learning-history` `daily_activity`. Do NOT create a second
   chart component.
3. **Recent Activity** — `RecentActivity.svelte` (Task 11) from
   `/analytics/dashboard` `recent_activity`; each item rendered as
   "Completed <step> in <path>" via i18n with a relative date
   (minutes/hours/days ago labels in en/ar); empty state uses an i18n string.
   (Inspect the live item shape first from `src/backend/services/analytics_service.py` —
   compose the sentence from real fields if it lacks a prebuilt text.)
4. **Your Paths** — one PathCard per path from `/paths/`, each with its
   progress meter sourced from `/analytics/dashboard` `path_progress` matched
   by path id (fall back to `Path.progress`), plus a "View analytics"
   button/CTA linking to `/analytics` (i18n). Empty state (no paths) with a
   CTA to the wizard (reuse existing keys where possible).

Page stays < 300 lines; blocks that grow large go into the Task 11
components.

Acceptance: `pnpm check` 0/0 in `src/frontend`; `pnpm build` clean; smoke
against real backend: both locales, non-zero learning hours on seeded data,
activity chart renders bars, RTL no horizontal overflow.

### Task 11: New components StatCard + RecentActivity

`src/frontend/src/lib/components/StatCard.svelte` and
`src/frontend/src/lib/components/RecentActivity.svelte` (each < 300 lines,
Svelte 5 runes, i18n-injected or via `t()`, no hardcoded strings). Follow
existing component conventions. StatCard: label, value, hint, optional icon,
muted style. RecentActivity: renders the feed + empty state; relative-date
formatting bilingual (use the existing i18n locale switch).

Acceptance: `pnpm check` 0/0; components render on the dashboard.

### Task 12: Dashboard i18n — extend, fix stepsOf, delete dead dashboard.* block

Edit `src/frontend/src/lib/i18n/messages/en.json` and `ar.json`:

1. **Fix `dashboardPage.stepsOf`** — currently `"/"` in BOTH files
   (en.json ~line 691, ar.json ~line 170) and rendered with `{done, total}`.
   Replace with a real format in both: en `"{done} of {total} steps"`, ar
   `"{done} من أصل {total} خطوات"` (match the file's interpolation style).
2. **Delete the dead `dashboard.*` block** — 24 keys in BOTH files
   (en.json lines 186-211; ar.json lines 326-350). Confirmed 0 usages. Remove
   the entire top-level group from both files.
3. **Extend `dashboardPage.*`** with the keys the redesign needs (KPI labels,
   master/skills/velocity, thisWeek, recent activity sentence parts, relative
   date units, viewAnalytics, completedStepsOf etc.) — keep the SAME key set
   in both files; remove now-unused `dashboardPage.*` keys if the redesign
   stopped using them (verify via grep; keep only live keys + the ones kept
   for reuse elsewhere, e.g. `dashboardPage.newPath` is used by learn page —
   do not delete cross-page keys).

Acceptance: en/ar flattened key sets identical (inline node/python parity
check); grep shows no `t('dashboard.` references anywhere in src; `pnpm
check` 0/0.

→ Phase C complete: **dashboard redesign** (verify pnpm check/build; smoke EN
+ AR: hours non-zero, activity populated, chart bars, RTL no-overflow).

---

## Phase D — Learner-app validation rollout

### Task 13: Validators library + validation i18n (frontend)

Create `src/frontend/src/lib/validation/validators.ts` (and a tiny
`src/frontend/src/lib/validation/index.ts` re-exporting it) — hand-rolled,
no deps, mirrors backend rules per Spec §6: email, name (1..100, forbids
`<>"'\\`), password policy {min_length (default 8), require_uppercase/
lowercase/digit/special_char (default true)} validated against the policy
object (param defaulting to DEFAULTS), lengths 100/150/200/2000, ranges
0-5 / 1-80 / 1-10 / 0-100 / ≥0, URL `http(s)://` parsing, hex color, options
≥2. Each validator returns `string | null` (error key or null) — the i18n
`t()` resolves keys. Provide a small `validateForm(schema)` helper: given
`{field: [value, validator]}` returns `{field: errorKey|null}`.

i18n EDIT `src/frontend/src/lib/i18n/messages/en.json` + `ar.json`: add a
`validation.*` group (reuse/extend the existing single `validation.
passwordsNoMatch`) covering every validator: required, emailInvalid,
nameChars, nameTooLong, minLength (param), policyRequirements (param),
maxLength (param), range (param), urlInvalid, hexColorInvalid,
minOptions, weeklyHoursRange, whitespace. Keep en/ar sets IDENTICAL.

Acceptance: `pnpm check` 0/0; parity check clean.

### Task 14: Wire learner forms with hints + live errors + blocked submit

Files (each < 300 lines):
`src/frontend/src/routes/(auth)/register/+page.svelte`,
`(auth)/login/+page.svelte`, `(auth)/forgot-password/+page.svelte`,
`(auth)/reset-password/+page.svelte`, `(app)/profile/+page.svelte`
(change-password + profile blocks), `(app)/wizard/+page.svelte`.

Wire per form (through the existing `error` prop on `Input.svelte`):
- register: name (1..100 + forbidden chars), email format, password policy →
  hint + live per-field error; submit blocked until valid.
- login: email format + password required; submit blocked until valid.
- forgot: email format; button blocked until valid.
- reset: password policy (new password) with hint; blocked until valid.
- change-password: current required, new password policy, confirm matches
  new (reuse `validation.passwordsNoMatch`); blocked until valid.
- profile: name (1..100 + forbidden chars), email format; blocked until valid.
- wizard: weeklyHours input gets min1/max80 + live error + hint when out of
  range (keep the generate-side floor coerce); role search gets a "type to
  search roles" hint (i18n); levels stay as-is (already ranged 0-5).

All strings i18n. No new deps. Keep backend as the policy authority — client
errors are UX, server errors still surface via toast/fieldErrorsFrom.

Acceptance: `pnpm check` 0/0; `pnpm build` clean; manual: each form blocks
invalid submit and shows bilingual hints/errors; parity en/ar clean.

→ Phase D complete (verification as above; smoke 3 validation forms EN+AR).

---

## Phase E — Admin-app validation rollout

### Task 15: Admin validators library + admin validation i18n

Mirror Phase D for `src/admin-app`: create
`src/admin-app/src/lib/validation/validators.ts` + index re-export (same
rules, including the admin-relevant extras: numeric FK ids positive int,
passing score 0-100, options ≥2, hex color, URL scheme). Reuse the
`fieldErrorsFrom` mapping for server 422s (existing). EDIT admin en/ar.json:
add/complete `admin.validation.*` group (and/or top-level `validation.*`
shared rules) — SAME keys both files.

Acceptance: `pnpm check` 0/0 in admin-app; parity clean.

### Task 16: Wire admin login + all CRUD dialogs with validation

Files (each < 300 lines): `src/admin-app/src/routes/+page.svelte` (login),
and the CRUD pages `(app)/users`, `(app)/skills`, `(app)/categories`,
`(app)/job-roles`, `(app)/resources`, `(app)/assessments`, plus the
assessment-questions dialog
(`src/admin-app/src/lib/components/assessment-questions-dialog.svelte`).

Rules per entity (mirror backend + Spec §6): users (email format, name ≤100
+ forbidden chars, password policy on create), skills (name ≤100 + nonempty,
description ≤2000, difficulty 0-5, cost hours ≥0, icon/color hex),
categories (name ≤100 + forbidden, description ≤2000), job-roles (title ≤100
+ forbidden, career_field ≤150, description ≤2000), resources (title ≤100 +
forbidden, url http(s), author/language ≤150), assessments (title ≤100 +
forbidden, description ≤2000, pass_score 0-100), questions (prompt ≤2000,
options ≥2 each ≤500, correct_option index valid, per-skill/assessment FK
positive ints).

Wire like Phase D: required, maxlength/max, numeric `inputmode`, hex, URL
scheme → hint + live inline error (`error` prop), submit/dialog-Save blocked
until valid. Backend stays authority; server 422 → `fieldErrorsFrom` inline
behaviour unchanged.

Acceptance: `pnpm check` 0/0 in admin-app; `pnpm build` clean; manual smoke:
open each dialog, invalid inputs show bilingual errors and block save.

→ Phase E complete (runs after D's i18n block to avoid file conflicts only
if sharing admin files — it shares none with Phase D; dispatch any time
after Phase B).

---

## Phase F — Final verification

### Task 17: Full verification pass

Run (from repo root / app dirs as applicable):
- `PYTHONPATH=src python -m pytest tests/ -q` → full suite green.
- `cd src/frontend && pnpm check && pnpm build` → 0/0 + clean build.
- `cd src/admin-app && pnpm check && pnpm build` → 0/0 + clean build.
- i18n parity both apps (inline en/ar flattened-key-set comparison → identical).
- `git diff` staging audit + `git status` — confirm only intended files
  staged/committed; confirm `src/data/settings.json` untouched (feature-flag
  state restored).
- Confirm 0 hardcoded `t(` gaps and the dashboard / feature-flags pages stay
  < 300 lines.

Report a verified-evidence table (command, exit, key output lines).

### Task 18: Final whole-branch review

Dispatch the final code reviewer over the whole plan's branch diff (review
package over `merge_base..HEAD`), pointing at the ledger's parked/deferred
list. Adjudicate residual findings: park with rulings or fix with ONE fix
subagent + one scoped re-review. Then present results; merge ONLY on request.

---

## Preflight conflict scan

Shared-file matrix (task rows: produce → consume):

| Files | Task pairs | What one makes vs what the other needs | Found |
|---|---|---|---|
| `backend/services/settings_schema.py` | T1 creates; T3,T4,T5 consume | New file; consumers follow Task 1's API | Sequential within Phase A — no conflict; T3/T4/T5 briefs carry the T1 API contract |
| `backend/services/settings_service.py` | T2 (adds get_all/reset_cache); T3,T4 consume; T5 monkeypatches | Same file, sequential tasks | Sequential — dispatch order 1..5 |
| `backend/routers/admin.py` | T3 rewires flags; T5 updates its tests | — | Sequential |
| `backend/routers/auth.py` + `services/auth_service.py` + `dto/auth.py` | T3 may touch auth error shape; T4 wires readers; T5 tests readers | Auth touched by 3 tasks | T3 limited to 422 detail shape (check only); T4 then T5 sequential — no concurrent edit |
| `backend/main.py` + `routers/realtime.py` | T4 (SSE quiet, limiter startup); T5 may assert | — | Sequential |
| `tests/test_settings.py` / `test_admin.py` | T1,T2 leave alone; T5 extends | — | Sequential |
| Classmates of existing suites (test_ai_*, test_wizard_analysis) monkeypatch `settings_service.is_ai_enabled` | T2/T4 change settings_service + auth_service | Setting reads must keep defaults identical so monkeypatches still pass | Whole-suite run at T5 + T17 gate this |
| `admin-app/.../feature-flags/+page.svelte` | T6 (knob fix), T7 (rewrite), T8 (extract) | Sequential same-file rewrites | Sequential 6→7→8; T7/T8 briefs carry pre-existing 114-line page state |
| `admin-app/src/lib/i18n/messages/{en,ar}.json` | T9 (flags+validation), T15 (validation), B-ui strings from T6-8 | Same two JSON files, sequential phases | B (T9) then E (T15) — sequential, no conflict |
| `frontend/.../dashboard/+page.svelte` | T10 (rewrite), T11 (components consumed by T10) | T10 consumes T11; same phase | Dispatch T11 FIRST then T10? No — T10 can be built with known props; dispatch T10 then T11-refactor OR T11 then T10-wire. Plan: dispatch T11 (components) then T10 (page wiring). Sequential |
| `frontend/src/lib/i18n/messages/{en,ar}.json` | T10 (dashboardPage keys), T12 (stepsOf/dashboard.*/extensions), T13 (validation.*) | Same two JSON files across Phase C and D | ⚠️ **Plan conflict:** user text said C + D parallel ("different files") but both edit the SAME `messages/{en,ar}.json`. **Ruling R-C/D:** run Phase C (10-12) then Phase D (13-14) SEQUENTIALLY. Cost if wrong: longer wall-clock (no parallelism between C and D). |
| `frontend/src/lib/validation/*` | T13 creates, T14 consumes | — | Sequential (T13 then T14) |
| `admin-app/src/lib/validation/*` | T15 creates, T16 consumes | — | Sequential (T15 then T16) |
| learner + admin apps (different dirs) | Phase D vs Phase E | No shared files (each app has own validation dir + own messages JSON) | **Parallel-safe** — matches user text "D, E parallel" |
| `src/data/settings.json` | All flag tests / smokes | Runtime-touched only | NEVER commit; restore after smoke (constraint 10) |

Rulings made before execution:

- R-1 (work-in-place): NO worktree. User-text stated; working tree carries the
  base redesign. Cost if wrong: bad edits are harder to unwind (no isolation).
- R-2 (commit strategy): task commits stage their named files wholesale;
  pre-existing uncommitted deltas on those files ride inside. Reviewers told
  the factual pre-existing state per task.
- R-3 (C/D sequential): user text's "C, D parallel (different files)" is wrong
  for the i18n JSONs (both edit `frontend/src/lib/i18n/messages/{en,ar}.json`);
  same-file concurrent edits produce git conflicts. Ruled sequential. Cost if
  wrong: slightly longer wall-clock.
- R-4 (cors_origins restart): CORSMiddleware config is built at startup;
  making it live requires poking middleware internals → editable but
  `live:false, restart:true` (applies-after-restart badge). Cost if wrong:
  admins must restart after CORS edits (documented in UI badge).
- R-5 (password_policy live): PasswordValidator reads live policy per call;
  client-side learner validator mirrors DEFAULT policy constants (learner app
  does not fetch admin flags). Backend remains the authority. Cost if wrong:
  a changed policy could pass client-side but fail server-side (server error
  still shown via existing toast/fieldErrors path).
- R-6 (dashboard hint source): "completed/remaining steps" computed from the
  already-fetched `/paths/` list (`Path.steps[].is_completed`), since the
  redesigned page drops `/progress/dashboard`. Cost if wrong: sum equals the
  authoritative per-step stats only if `/paths/` returns full steps (it does
  — PathCard already consumes `path.steps`).
- R-7 (ActivityBarChart): reuse the existing component; do NOT create a
  second one. Cost if wrong: a duplicated chart would violate scope discipline.
- R-8 (ai_path_generation / app_mode / csrf_protection): read-only (not
  editable) per Spec §3; `ai_path_generation` stays a mirror of `ai_enabled`.
  Cost if wrong: these remain display-only, matching today.
- R-9 (limiter import): if `routers/admin.py` importing `limiter` risks a
  circular import, import lazily inside the PUT handler; verify at build.
- R-10 (auth expiry constant): session timeout must be read at token-
  issuance time, not baked at import. Auth_service gets a small reader.
  Cost if wrong: a flag change wouldn't affect new tokens until restart.

## Task-to-dispatch order

Phase A (sequential): 1 → 2 → 3 → 4 → 5.
Phase B (sequential): 6 → 7 → 8 → 9.
Phase C (sequential): 11 (components) → 10 (page) → 12 (i18n).
Phase D (sequential): 13 → 14.
Phase E (sequential, any time after B): 15 → 16.
Phase F: 17 → 18.

Each task: one implementer dispatch, one task review (spec + quality), fix
rounds on findings, ledger the completion line. Dispatch dependencies that
share files strictly sequentially (every pair above shares a file or is a
consumer/producer). The interleaving E can run after B completes (different
app); but to keep the controller simple, run phases in alphabetical order.
Final whole-branch review at the end (Task 18).

Estimated task scale: 13+ sub-agents per AGENTS.md guideline.