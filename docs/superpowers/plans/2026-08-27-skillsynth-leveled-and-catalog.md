# SkillSynth — Error Fix + Leveled Per-Skill Testing + Category Surfacing

## Objective
Fix the persistent frontend console error in the admin app (root cause: browser extension calls a non-existent hook — web-vitals-related — NOT a code bug, per final diagnosis), add leveled per-skill testing (fail-lower / pass-level-up loop driven by `assess_service.review_level`), and surface the dormant categories (no skills attached) via a new public catalog router + analytics progress-by-category, with bilingual AR/EN UI.

## Tech Stack
- Backend: FastAPI + SQLAlchemy (Clean Architecture), `from backend import X` imports.
- Frontend (student) & Admin app: **SvelteKit 5 + Svelte 5** (NOT Next.js — see Rulings).
- DB: SQLite dev / Postgres prod, 15-table 3NF.
- i18n: `src/frontend/src/lib/i18n/messages/{en,ar}.json` (NOT `src/frontend/src/lib/i18n/{en,ar}.json` — see Rulings).

## Global Constraints
- Every change MUST keep `skillsynth verify` (frontend+admin svelte-check, frontend+admin build, pytest, schema, doctor) green after every task.
- No function > 40 lines; every function carries a docstring stating purpose + caller/callee.
- No file > 300 lines (seed_v4.py is the documented exception).
- JSON columns limited to the 4 documented exceptions; do NOT add JSON to new tables/columns.
- ADR-015: AI may only adjust proficiency ±1 at confidence==high, clamped 0..5; deterministic scoring/topo-sort never overwritten. AI_ENABLED=false → seeded fallback (no llama-cpp import).
- ADR-014: referential integrity → 400 (bad FK naming), 409 (rename-uniqueness case-insensitive, category/prereq cycle, restricted deletes unless `?force=true`).
- RTL-first; 0 hardcoded user-facing strings; dynamic RTL/LTR; Tajawal font.
- Package manager: pnpm for frontend/admin.
- Never dispatch sub-subagents; review arrives from controller.

## Design Decisions (confirmed)
- Higher-level topic generation uses dynamic AI `generate_skill_topics` (seeded fallback when AI disabled), not pre-seeded DB topics.
- Each step opens with a baseline test at the selected level; loop = fail-lower / pass-level-up (via `assess_service.review_level`).
- Per-skill wizard `levels` = starting level per skill (goal skills only).

## Rulings (pre-flight conflict scan — MUST be honored by subagents)
- **R-A (AGENTS.md stale):** Codebase is SvelteKit 5, not Next.js. Follow this plan; ignore AGENTS.md's Next.js claims.
- **R-B (Part 1 mostly no-op):** admin-app has NO `next.config.*`, NO `pages/`, NO eslint config, NO `next` dependency. Tasks 1.1/1.2/1.3 are no-ops; the migration is already done. Part 1 = Task 1.4 verification + Task 1.5 note.
- **R-C (AI gate):** `is_ai_enabled()` does NOT exist. Use `from backend.config.app_settings import AI_ENABLED` combined with `llm_pipeline._engine_available()`.
- **R-D (catalog helpers):** `catalog_service` has `_serialize_skill(db, skill)` only (NO `_category_out`). `catalog_repository` HAS `get_all_categories` + `get_all_skills` but NO `get_skills_by_category`. Subagent adds `get_skills_by_category(db, category_id)` (filter `skills.category_id`) and a category serializer (new `_serialize_category` in service or inline in router).
- **R-E (schema gate):** `verify_schema.py` compares DDL↔ORM dynamically — NO hardcoded expectation set. Edit ONLY `003_reduced_schema.sql` + `PathStep` entity. Do NOT edit `verify_schema.py`. Mirror `NOT NULL DEFAULT 0` / `nullable=False, default=0` exactly.
- **R-F (i18n path):** Keys live at `src/frontend/src/lib/i18n/messages/{en,ar}.json`.
- **R-G (naming):** `current_level` exists in unrelated DTOs (`GapItem`,`GapPrerequisite`)/analytics; adding `selected_level`/`current_level` to `PathStep`+`StepOut` is safe (different models).

---

## Part 1 — Error Fix (web-vitals / startTime)

### Task 1.1
Verify no stale Next.js config remains in `src/admin-app/`: confirm absence of `next.config.js`/`next.config.mjs`/`next.config.ts` and a `pages/` directory. If found, delete them. Expected outcome: none found (migration already complete). Report what was checked.

### Task 1.2
Confirm `src/admin-app/` has no eslint config extending `next/core-web-vitals` or referencing `next` plugin (e.g. `.eslintrc.cjs`, `.eslintrc.json`, `eslint.config.js`). Report; fix only if a stale config exists.

### Task 1.3
Confirm `src/admin-app/package.json` does NOT list `next` (and no `eslint-config-next`, `eslint-plugin-next`). If present, remove and run `pnpm install`. Expected: already absent.

### Task 1.4
Run `./skillsynth verify` from repo root. Confirm admin + frontend svelte-check/build pass. Grep the build output (`.svelte-kit/output` and `build/`) for the literal string `reportAllChanges` — expect ZERO matches (no stale extension hook). If found, treat as blocker and report. Report the verification result.

### Task 1.5
Document (in the final PR summary / this branch's notes) the root cause: the console error is from a browser extension invoking a `web-vitals`-related `onLCP`/`onFCP`/`onCLS` hook that the app does not define; it is NOT a code defect. No code change required. Note the fix-if-real instruction: only add a no-op exported hook if a genuine in-app reference is later confirmed.

---

## Part 2 — Leveled Per-Skill Testing

### Task 2.1
In `src/backend/dto/learning.py`:
- `GeneratePathIn`: add `levels: dict[str, int] = {}` (skill name → desired starting level 1..5; only goal skills honored).
- `DetailedPreferences.format`: change type from `Optional[str]` to `str | list[str]` default `"any"` (accept one or many).
Keep all existing fields. Update any validation that assumed `format` was a single string.

### Task 2.2
Schema + entity for leveled steps:
- `src/migrations/003_reduced_schema.sql`: add to `path_steps` table:
  `selected_level INTEGER NOT NULL DEFAULT 0`, `current_level INTEGER NOT NULL DEFAULT 0`.
- `src/backend/entities/learning.py` `PathStep`: add `selected_level = Column(Integer, nullable=False, default=0)` and `current_level = Column(Integer, nullable=False, default=0)`.
- `seed_v4.py`: no row change needed (defaults 0); ensure `_seed_paths`/plan persistence sets them (Task 2.3).
- Do NOT edit `verify_schema.py` (see R-E). After: `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH.

### Task 2.3
In `src/backend/services/learning_service.py` `generate_path` (and `_persist_plan`):
- Read `GeneratePathIn.levels` (dict skill-name → level).
- When persisting each `PathStep`, set `selected_level = levels.get(skill.name, current.get(skill.name,0))` and `current_level = selected_level` initially.
- `_pick_resource_ids`: when `preferences.format` is a list, accept a resource whose `format` is in the list (previously only exact-string match). Keep "any" behavior.
- Return `levels` back in the response (add `levels` to the path DTO/response).

### Task 2.4
In `src/backend/services/step_test_service.py`:
- `compute_effective_difficulty(level, last_result)` already exists (lines ~60-72) — keep, ensure it lowers difficulty on recent fail and raises on recent pass.
- `generate_step_test(plan_id, step_id, db, ai_enabled, level)` (lines ~98-148): add a `level` parameter; pass difficulty = computed from current_level; for levels > 1, generate topic via `llm_pipeline.generate_skill_topics(skill_name, level)` when AI enabled, else seeded fallback (`f"Topic {i} for {skill} (level {level})"`). Keep deterministic seed fallback.
- `grade_step_test(answers, correct_map, db, user_id, plan_id, step_id)` (lines ~151-251): use `assess_service.review_level(correct, total, difficulty, attempt_no, current_level)` to compute next level; return `next_level` plus a `passed` flag (passed if next_level >= previous after a pass, i.e. level-up or held at top).

### Task 2.5
In `src/backend/services/step_test_service.py` `generate_step_test`: gate AI calls with `from backend.config.app_settings import AI_ENABLED` AND `llm_pipeline._engine_available()` (NOT `is_ai_enabled()`, which does not exist). When disabled, use seeded fallback topics.

### Task 2.6
Tests for leveled loop in `tests/` (new or extend `test_step_test.py`):
- `compute_effective_difficulty`: lower on fail, raise on pass.
- `generate_step_test`: level 1 uses seeded topics; level>1 with AI disabled uses seeded fallback (mock `_engine_available` false).
- `grade_step_test`: fail lowers level, pass at top holds, pass below top raises; returns `next_level`.
- `learning_service.generate_path` honors `levels` dict and list `format`.
Assert real behavior (no vacuous asserts).

### Task 2.7
In `src/backend/routers/paths.py` and `routers/learning.py`:
- `POST /api/generate-path/` accepts `levels` per skill; persists via `generate_path`.
- `GET /api/paths/{id}` (learn page load) step serializer includes `selected_level` and `current_level` (add to `StepOut` DTO in `dto/learning.py` if missing).
- `POST /api/steps/{step_id}/test` (or existing step-test route) returns the test at `current_level`; response includes `difficulty` and `level`.
- `POST /api/steps/{step_id}/grade` returns `next_level` + `passed`; on level-up set `current_level = next_level` on the `PathStep`.

### Task 2.8
In `src/backend/services/llm_pipeline.py`:
- Add `generate_skill_topics(skill_name: str, level: int) -> list[str]` (lines ~158-183): if `AI_ENABLED and _engine_available()`, call the LLM with a prompt requesting `min(3, level+1)` level-appropriate topics; else return seeded fallback. Wrap in `LLMOperationError` handling consistent with `generate_skill_quiz`.
- (No `is_ai_enabled()` to add — use `AI_ENABLED` + `_engine_available()` per R-C.)

### Task 2.9
Frontend: `src/frontend/src/routes/(app)/learn/[id]/+page.svelte`:
- Load path; for each step show a **level ladder** (1..5) reflecting `current_level`/`selected_level`.
- On step open, fetch the baseline test (`current_level`); render via `QuizRunner.svelte`.
- After grading, show result + "Level up" / "Try again (lower)" affordance based on `next_level`/`passed`.

### Task 2.10
i18n: add `learn.*` keys to `src/frontend/src/lib/i18n/messages/{en,ar}.json`:
- `learn.level`, `learn.levelLadder`, `learn.baseline`, `learn.levelUp`, `learn.tryAgainLower`, `learn.testAtLevel`, `learn.passed`, `learn.notPassed`. AR translations required (parity).

### Task 2.11
Verify Part 2 end-to-end: `./skillsynth verify` green. Manual smoke (optional): generate a path with `levels={"<skill>":3}` and confirm step persisted with `selected_level=3`. Add/adjust backend tests so `PYTHONPATH=src python -m pytest tests/ -q` passes.

---

## Part 3 — Surface Dormant Categories

### Task 3.1
Create `src/backend/routers/catalog.py` (public, NOT admin):
- `GET /api/catalog/categories` → `catalog_repository.get_all_categories()` serialized (new `_serialize_category` in `catalog_service` or inline; do NOT call non-existent `_category_out`).
- `GET /api/catalog/categories/{id}/skills` → `catalog_repository.get_skills_by_category(db, id)` via `_serialize_skill`.
- `GET /api/catalog/skills` → all skills (`get_all_skills` + `_serialize_skill`).
- `GET /api/catalog/skills/{id}` → single skill.
Add router to `src/backend/main.py` under `/api/catalog`. (Admin catalog already lives in `catalog_admin.py`; do not touch it.)

### Task 3.2
In `src/backend/repositories/catalog_repository.py` add `get_skills_by_category(db, category_id) -> list[Skill]` filtering `skills.category_id == category_id`. Keep under 40 lines, docstring included.

### Task 3.3
In `src/backend/services/catalog_service.py` add `_serialize_category(db, category) -> dict` (id, name, description, parent_id, skill_count optional). Keep `_serialize_skill` as the skill serializer.

### Task 3.4
Analytics: wire `analytics_service.progress_by_category(db, user_id)` (exists ~line 255) to a new endpoint `GET /api/analytics/progress-by-category` in `routers/analytics.py`. Return per-category mastery (counts of skills at level≥target, average current_level, etc.). Reuse existing logic; do not duplicate.

### Task 3.5
i18n: add `catalog.*` and `analytics.*` keys to `src/frontend/src/lib/i18n/messages/{en,ar}.json`:
- `catalog.categories`, `catalog.skillsInCategory`, `catalog.browseByCategory`, `catalog.emptyCategory`.
- `analytics.progressByCategory`, `analytics.categoryMastery`, `analytics.averageLevel`.
AR parity required.

### Task 3.6
Frontend: add a public catalog browse view (route e.g. `src/frontend/src/routes/(app)/catalog/+page.svelte` or integrate into explore):
- List categories (from `/api/catalog/categories`), clicking shows skills in that category.
- Surface dormant categories (those with 0 skills) with a clear "no skills yet" state using `catalog.emptyCategory`.
- Optionally show `progress-by-category` on the dashboard using `analytics.*` keys.
Keep design consistent with the Linear/Notion style, RTL-first, bilingual. `./skillsynth verify` green.

---

## Verification Gate (every task)
`./skillsynth verify` (frontend+admin svelte-check, frontend+admin build, pytest, schema, doctor) MUST stay green. `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH after Task 2.2.
