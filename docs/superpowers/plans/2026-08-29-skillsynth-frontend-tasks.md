# SkillSynth: frontend tasks — assessment removal, real durations, analytics redesign, CTA polish

Branch: `feature/leveled-testing-and-catalog` (work in place, NO worktree — the
working tree carries a large body of pre-existing UNCOMMITTED redesign work that
these files build on; same ruling as prior plans on this branch).

BASE for Task 1 dispatch: `67f19251fd5e07fb0a17c7d933eb241e1f7000d5` (HEAD at plan start).

All work is frontend-only on the student SvelteKit app at `src/frontend`. No
backend changes (nothing under `src/backend/`, no schema/seed/DTO changes).

## Global Constraints

1. **Frontend-only.** No files under `src/backend/`, no `run.py`, no schema or
   seed changes, no backend tests touched.
2. **Verification commands** (run from `src/frontend`, i.e. workdir; the repo has
   NO frontend test runner — package.json exposes only dev/build/preview/check):
   - `pnpm check` → svelte-check: 0 errors, 0 warnings (current baseline already clean)
   - `pnpm build` → clean build
   - i18n parity: the key SET in `en.json` must equal the key SET in `ar.json`
     (compare against each other; every addition/removal lands in BOTH files)
   - grep-based assertions where the task names one (e.g. no lingering references)
3. **i18n.** Every user-visible string is an i18n key from
   `src/frontend/src/lib/i18n/messages/{en,ar}.json`. 0 hardcoded strings. Reuse
   existing keys (`units.*` etc.) where sensible. RTL-first bilingual design stays intact.
4. **Design system.** Linear/Notion/Stripe style. No neon, no gradients, no
   glassmorphism. Use the existing CSS tokens (`--accent-deep`, `--ochre-deep`,
   `--paper`, `--paper-2`, `--line`, `--line-strong`, `--muted`, `--danger`, `--sage`,
   `--radius`, `--font-display`). Layout must not break under `dir=rtl`.
5. **File size.** Any file created or grown stays under 300 lines.
6. **Scope discipline.** Do exactly what the task says. Do not restructure or
   "improve" unrelated code in the touched files. Follow existing Svelte 5 runes
   patterns (`$state`, `$derived`, `$effect`) and existing component/API-client
   conventions in `src/frontend/src`.
7. **Commit hygiene.** Stage ONLY the files the task names (git add the exact
   paths). The working tree is deliberately dirty with unrelated in-progress work
   (docs, AGENTS.md, .gitignore, backend tests, admin-app/.svelte-kit artifacts,
   etc.) — NEVER stage or commit anything outside the task's file list, and NEVER
   stage `.env*` files. Commit per file-scoped change with a conventional message
   (`feat:`/`fix:`/`chore:`/`refactor:`), matching repo style.
8. **Plans are the authority.** If a task's text conflicts with these constraints,
   the constraint wins and the implementer reports the conflict.

## Task 1: Delete the header "Assessment" button and the TakeQuizDialog feature

Frontend feature removal. Files:

1. `src/frontend/src/routes/(app)/learn/[id]/+page.svelte` (path detail — 347 lines).
   Remove ONLY the TakeQuizDialog-feature wiring; leave the QuizRunner-based flows:
   - Line 16: `import TakeQuizDialog from '$lib/components/TakeQuizDialog.svelte';`
   - Line 26: `let showQuiz = $state(false);`
   - Line 31: the `skills` `$derived` (`(path?.steps ?? []).map(...)` with `{ id, name }`)
     — its only consumer is the dialog's `{skills}` binding.
   - Lines 88–92: `handlePracticeTestStart` — its only caller is the dialog's `onstart`.
   - Line 242: the header button `<Button onclick={() => (showQuiz = true)}><Icon name="sparkles" size={16} />{t('wizard.assessmentTitle')}</Button>`
   - Line 310: `<TakeQuizDialog bind:open={showQuiz} {skills} onstart={handlePracticeTestStart} />`
   - KEEP: `showQuizRunner`, `quizTest`, `quizStep`, `diagnostic`,
     `onAiTestReady`, `submitStepTest`, `submitPracticeTest`, `onQuizResult`, and the
     `QuizRunner` usage (lines 312–321) plus the SSE listeners (lines 44–64). The
     step-test and AI practice-test flows stay fully functional.
   - Before removing each symbol, confirm no remaining reference exists in the file.
2. Delete the file `src/frontend/src/lib/components/TakeQuizDialog.svelte`
   (git rm / git add -A on that exact path).
3. `src/frontend/src/lib/i18n/messages/en.json` and `ar.json`: remove the two
   `wizard.*` keys (kept in parity across BOTH files):
   - `wizard.assessmentTitle`
   - `wizard.startAssessment`
   KEEP `wizard.summaryGoal` and any other `wizard.assessment*` keys — a different feature.

Acceptance:
- `pnpm check` → 0 errors, 0 warnings; `pnpm build` clean.
- `rg -n "TakeQuizDialog|showQuiz|handlePracticeTestStart" src/frontend/src` → no matches.
- `wizard.assessmentTitle` / `wizard.startAssessment` absent from BOTH en.json and
  ar.json; en/ar key sets remain identical; QuizRunner still mounted (grep the
  file for QuizRunner).

## Task 2: Show the path's real estimated duration

In `src/frontend/src/routes/(app)/learn/[id]/+page.svelte` (347 lines):
- Stats duration Panel (currently line 247), which sums step durations:
  `{Math.round((path.steps ?? []).reduce((a: number, s: any) => a + (s.duration_hours ?? 0), 0))}h`
  Replace with the authoritative backend value `path.total_estimated_hours ?? 0`,
  formatted (e.g. `42h`, or `42` hours). If `path.total_estimated_weeks` is present
  and truthy, additionally render it using a suitable existing `units.*` i18n key if
  one exists, else add one minimal key in BOTH en/ar.
- Per-step meta line (currently line 274) prints `{step.duration_hours ?? 0}h`
  unconditionally — change so it prints `Nh` ONLY when `step.duration_hours` is
  truthy. Keep the ` · ` separators consistent: a step without a duration shows no
  empty value and no leading/trailing stray separator for it.
- No backend change. If an i18n key is added, it exists in en.json AND ar.json.
- Acceptance: `pnpm check` 0/0; `pnpm build` clean; a step with no
  duration_hours renders no "0h"; the stats panel shows the path's authoritative
  total, not a per-step sum.

## Task 3: Comprehensive analytics redesign (plain CSS/SVG, no chart library)

Rework `src/frontend/src/routes/(app)/analytics/+page.svelte` (currently ~103
lines, minimal) into a comprehensive dashboard. No chart library — plain CSS and
SVG only. No new npm dependency.

Data sources (all already provided by the backend; use the existing API client at
`src/frontend/src/lib/api/client.ts` — read it first for the exact call helpers):
- `/api/analytics/dashboard` → completion rate, mastered skills count, learning
  velocity (per week), total learning hours, and `path_progress` (per-path list,
  currently returned but unused in the page).
- `/api/analytics/learning-history` → `daily_activity` (last-7-days
  `[{date, count}]`) for the This-week chart.
- `/api/learning/analysis` → strengths vs weaknesses (two columns).
- `/api/analytics/skill-growth` → `knowledge_gaps`.
- Keep/reuse the existing skill-mastery presentation via
  `src/frontend/src/lib/components/TopSkills.svelte` in the layout.

Layout (bottom-up, no invention of data):
1. KPI row — 4 cards: Completion Rate, Mastered Skills, Learning Velocity (/wk),
   Total Learning Hours.
2. "This week" — 7-day bar chart from `daily_activity`; implement as a new small
   component `src/frontend/src/lib/components/ActivityBarChart.svelte` (plain
   CSS/SVG bars, day labels, < 300 lines, RTL-safe). Gracefully handle an empty
   list (e.g. a "no activity" short label via i18n).
3. Path progress — per-path horizontal progress bars from the dashboard's
   `path_progress` (currently unused); include an empty state when a user has no
   paths (i18n key, e.g. notStarted).
4. Two-column Strengths vs Weaknesses from `/api/learning/analysis`.
5. Knowledge Gaps list from `skill-growth.knowledge_gaps`.
6. Skill mastery — keep the TopSkills presentation.

i18n: add labels in BOTH en.json and ar.json, inside the existing `analytics`
key group (match the file's existing structure; e.g. thisWeek, dailyActivity,
strengths, knowledgeGaps, notStarted, remainingHours — choose exact key names
consistent with the existing analytics group and reuse `units.*` where possible).
0 hardcoded strings; en/ar key sets identical.

Acceptance: `pnpm check` 0/0; `pnpm build` clean; no new dependency; new component
< 300 lines; keys symmetric en/ar; page renders each of the 5 sections; existing
backend responses unchanged.

## Task 4: Polish the "New Path" CTA in the learn header

In `src/frontend/src/routes/(app)/learn/+page.svelte` (header area), the "New
Path" button currently links to the wizard.
- Keep it a primary-styled button holding the plus icon.
- Refine hover / focus-visible / active states and subtle prominence so it reads
  as the page's primary call-to-action. Small, deliberate polish. Scope any CSS
  change to the Button primary-variant styles — edit
  `src/frontend/src/lib/components/ui/Button.svelte` (primary-variant CSS only)
  if needed, but keep it surgical; do not restyle the component API or other
  variants.
- No neon, gradients, or glassmorphism. Use existing tokens.
- Acceptance: `pnpm check` 0/0; `pnpm build` clean; the button remains primary + plus
  icon; hover/focus/active states are visibly improved but consistent with the
  design system.

---

## Preflight conflict scan

Shared-file matrix (task rows = produce → consume):

| Files | Task pairs | What one makes vs what the other needs | Found |
|-------|------------|----------------------------------------|-------|
| `learn/[id]/+page.svelte` | 1 & 2 | T2 edits the file T1 removed dialog wiring from | Sequential (T2 dispatched after T1 committed) — no live conflict; T2 line numbers shift, brief labels by symbol not line |
| `i18n/messages/{en,ar}.json` | 1, 2, 3 | T1 removes 2 wizard keys; T2 may add 1 units key; T3 adds analytics keys | Different key groups; all sequential — no overlap |
| `ui/Button.svelte` | 4 (only) | — | Pre-existing 22+/12- uncommitted delta on the file predates this plan; T4 edits may stack on it |
| `learn/+page.svelte` | 4 (only) | — | Pre-existing 17+/1- uncommitted delta predates this plan; T4 edits stack on it |
| `analytics/+page.svelte` | 3 (only) | — | Pre-existing 6+/4- uncommitted delta predates this plan; T3 redesign overwrites it |
| `TakeQuizDialog.svelte` | 1 (only) | — | Pre-existing 28+/20- uncommitted delta; T1 deletes the file entirely |

Notes / rulings:
- R-1 (work-in-place): NO worktree — the working tree contains the large
  uncommitted redesign these files build on; a bare worktree off committed HEAD
  would lack them. Cost if wrong: bad edits are harder to unwind (no branch
  isolation).
- R-2 (commit strategy): implementers commit ONLY their task's named files,
  staging them wholesale (git is file-granular). Small pre-existing uncommitted
  deltas on Button.svelte / learn/+page.svelte / analytics/+page.svelte /
  TakeQuizDialog.svelte will therefore ride along inside those commits; task
  reviewers are told the factual pre-existing state so they scope findings to the
  task's actual change. Cost if wrong: a task commit may contain a few lines of
  another person's earlier edits, recoverable via git reset.
- R-3 (TDD not applicable): the frontend has no test runner (no vitest/jest in
  package.json). Verification = `pnpm check` + `pnpm build` + grep/i18n-parity
  assertions named per task. Cost if wrong: none — repo's own verification
  commands are used.
- R-4 (stale AGENTS.md): AGENTS.md describes a Next.js frontend; the real stack is
  SvelteKit 5 (confirmed at commit 4dca71bb). Follow the plan/codebase, not
  AGENTS.md's framework claims. Cost if wrong: n/a.

## Task-to-dispatch order

1. Task 1 (feature removal)
2. Task 2 (real durations) — after Task 1; same file, need sequential dispatch
3. Task 3 (analytics redesign)
4. Task 4 (CTA polish)

Each task: one implementer dispatch, one task review (spec + quality) after it,
fix rounds on findings, then next task. Final whole-branch review at the end.