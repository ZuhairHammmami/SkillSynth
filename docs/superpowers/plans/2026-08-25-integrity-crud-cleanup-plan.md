# Plan: Integrity-First CRUD Completion, Testing, Cleanup & Documentation Sync

Date: 2026-08-25 · Branch: `feature/smart-mentor-v1` (work continues in-place; one commit-set per task)

## User Decisions (binding)
1. Complete CRUD **end-to-end**: backend endpoints + admin UI edit dialogs.
2. Git reconciliation of the 293 pending changes: **commit**.
3. Documentation: **full rewrite** of numbered SS-EDS sections + prune stale/duplicate.
4. Cleanup: **delete** all stale/duplicate content (git history preserves committed versions).
5. Delete policy: shared reference data (skills, categories, job_roles) → **409 + dependent breakdown unless `?force=true`**; composition cascades (paths/steps/progress, assessments/questions/results, user-owned rows) unchanged.

## Global Constraints (every task)
- Python: functions ≤40 lines, each with a docstring stating its single purpose + caller/callee relationships; files <300 lines (`seed_v3.py` exempt); imports `from backend import X`; commands run with `PYTHONPATH=src`.
- Package manager: **pnpm** (`export PATH=$PATH:/home/zuhair/.npm-global/bin`). Frontend workdir `src/frontend`; admin `src/admin-app`.
- i18n: ar/en leaf-key parity must hold (583=583 today; may grow only in equal pairs).
- Wire-compat: existing endpoint URLs and response keys never change; only additive changes allowed.
- Tests: isolated temp DB (conftest rebinds engine/SessionLocal, seeds via `seed_v3.seed(engine=..., session_factory=...)`); dev `skillsynth.db` never touched; password literals must pass the validator (never "AdminMade@123"; use e.g. "Zephyr#7781kq").
- HTTP status semantics: **404** missing entity / **409** uniqueness-or-dependent conflict / **400** invalid reference or body.
- Verification baseline: `PYTHONPATH=src python -m pytest tests/ -q`; `PYTHONPATH=src python tools/verify_schema.py` (SCHEMA MATCH); `cd src/frontend && pnpm type-check && pnpm lint && pnpm build`; same for admin-app.
- No subagent may dispatch further subagents. Report files over chat summaries.

---

## Task 1: Reconcile git baseline — CONTROLLER EXECUTES DIRECTLY
Surgical triage; no implementer.
1. Snapshot `git status --short > /tmp/opencode/pre-reconcile.txt`.
2. Update root `.gitignore`: append `*.tsbuildinfo`, `skillsynth.db`, `*.db-journal`, `reports/archive/` NOT ignored (they get deleted physically in Task 6, not ignored). Then `git rm --cached src/admin-app/tsconfig.tsbuildinfo`.
3. Stage ALL tracked deletions + modifications (`git add -u`) — these are the old monolith/feature-sliced files removed on disk plus current app edits (database.py pooling/WAL, frontend redesign files, config files).
4. Add ONLY these untracked paths (active app): `.agents/skills/brainstorming/ executing-plans/ fastapi-python/ find-skills/ requesting-code-review/ systematic-debugging/ test-driven-development/ using-superpowers/ writing-plans/`, `.dockerignore`, `.env.example`, `Dockerfile`, `docker-compose.yml`, `src/frontend/Dockerfile`, `src/frontend/public/favicon.svg`, `src/frontend/src/app/(auth)/layout.tsx`, `src/frontend/src/app/(auth)/reset-password/page.tsx`, `src/frontend/src/app/(student)/`, `src/frontend/src/app/error.tsx`, `src/frontend/src/app/global-error.tsx`, `src/frontend/src/i18n/` (config.ts provider.tsx root-provider.tsx request.ts hooks.ts), `src/frontend/src/middleware.ts`, `src/frontend/src/shared/components/Loading.tsx LocaleSwitcher.tsx NewPathDialog.tsx PathWizard/`, `src/frontend/src/shared/hooks/useAuthApi.ts`, `src/frontend/src/shared/ui/combobox.tsx`.
   Do NOT add: `seed_v2.py`, `src/seed/`, `src/migrations/001_*.sql`, `002_rebuild_schema.sql`, `tools/audit_architecture.py db_reduction.py recovery_verification.py`, `CERTIFICATION/`, `PHASE_A/`, `PHASE_B/`, `reports/archive/ reports/rediscovery/ reports/qa-gate-final.md` (stale — physically deleted in Task 6).
5. Check `reports/qa-gate-final.md` vs committed `reports/qa-gate-schema-reduction.md`; if duplicate/superseded leave untracked (deleted in Task 6).
6. Commit: `chore: reconcile working tree to 15-table core`.
Gate: `git status --short` shows ONLY the known-stale untracked items; pytest 80 green; both builds green.

## Task 2: Backend CRUD wiring + integrity enforcement layer (TDD)
Write failing tests FIRST in `tests/test_admin.py` (+ `tests/test_catalog.py` where natural), then implement.

**A. Wire orphaned service/DTO methods into `src/backend/routers/admin.py`:**
- `PUT /api/admin/users/{user_id}` → `admin_service.update_user` (full_name, is_admin, optional password reset). Guard: cannot demote/deactivate self (`is_admin` False on self → 409).
- `PUT /api/admin/skills/{skill_id}` → `catalog_service.update_skill` (already returns (payload,error)); map errors: "not found"→404, "exists"→409.
- `PUT /api/admin/resources/{resource_id}` → `catalog_service.update_resource`.
- Category CRUD: `POST /api/admin/categories`, `PUT /api/admin/categories/{id}`, `DELETE /api/admin/categories/{id}?force=`.
- Job-role CRUD: `GET /api/admin/job-roles`, `POST`, `PUT /{id}`, `DELETE /{id}?force=` (list payload = `_serialize_job_role` incl. `skill_ids`).
- All admin routes keep `Depends(require_admin)`.

**B. Integrity enforcement (services + repos):**
1. FK existence validation before insert/update → 400 naming bad ref (`Unknown category_id=5`, `prerequisite_ids contains unknown skill ids: [7]`, `skill_ids contains unknown ids: [...]`). Applies: skill create/update (category_id, prerequisite_ids), category update (parent_id), resource create/update (skill_id), job-role create/update (skill_ids), assessment create path untouched (none wired).
2. Category parent rules → 400: self-parent; ancestor cycle (walk parent chain).
3. Prerequisite rules → 400: self-prereq; edge creating a cycle (DFS from candidate prereq through existing graph).
4. Rename-uniqueness guards (case-insensitive, matching existing ilike/exact conventions — standardize on ilike): skill name, category name, job-role title, user email (update_user), excluding the row itself → 409.
5. Restricted deletes: extend `catalog_service.delete_skill/delete_category/delete_job_role` to count dependents BEFORE deleting:
   - skill → counts in job_role_skills, user_skills, path_steps, resources, assessments, skill_prerequisites(both directions);
   - category → count skills;
   - job_role → count job_role_skills.
   Non-zero → return structured conflict `(False, {"dependents": {...}, "message": ...})` → router maps to 409 with JSON detail listing counts. `?force=true` (query bool) proceeds with existing DB cascade/set-null semantics.
6. Centralized safety net: exception handler in `main.py` mapping `sqlalchemy.exc.IntegrityError` → 409 JSON `{"detail": "...conflict..."}` after rollback (repos roll back or handler does `db.rollback()` via request middleware — prefer explicit try/except in the handler using a fresh check; keep ≤40-line functions).
7. Fix conflated messages: repo-level "not found" must surface 404 ("Skill not found"), reserve "might be in use" style text for real conflicts.

**C. TDD tests to write in Task 2 (unit-level, happy+error per rule above):**
rename duplicates ×4 entities; bad FK refs ×4; self-parent; ancestor cycle; self-prereq; prereq cycle; restricted delete ×3 (409 shape `{detail:{dependents:{...}}}`); force-delete happy path ×3; PUT happy paths ×5 (users/skills/resources/category/job_role); PUT 404s; demote-self guard.

House rules apply to every touched file; `admin.py` must stay <300 lines — if adding pushes past, split catalog-admin routes into `routers/admin.py` + new `routers/catalog_admin.py` mounted under `/api/admin` (wire-compat preserved) and note it in the report.

Gate: all new tests green; FULL suite green; both builds green; curl smoke: PUT skill rename-dup → 409, DELETE skill with learner rows → 409, `?force=true` → 200.

## Task 3: Admin UI edit dialogs + categories/job-roles management
App: `src/admin-app` (English-only, no i18n). Follow existing page/dialog patterns exactly (see `skills/create-skill-dialog.tsx`, `resources/create-resource-dialog.tsx`, users page table + dialog, react-query usage in `src/lib/api.ts` hooks pattern).
1. Edit dialogs (prefill + PUT on save, reuse create-dialog field schemas):
   - `users/edit-user-dialog.tsx` (full_name, is_admin toggle, optional new password w/ policy hint)
   - `skills/edit-skill-dialog.tsx` (name, description, difficulty_level, estimated_hours, icon, color, category select, prerequisite multi-select)
   - `resources/edit-resource-dialog.tsx`
2. New pages mirroring existing CRUD-page structure:
   - `/categories` — table + create/edit/delete-with-force-confirm dialogs
   - `/job-roles` — table (title, career_field, #skills) + create/edit (multi-select skills)/delete-with-force-confirm
3. Delete confirmations show dependent counts from the 409 response body and offer Force delete button (calls same endpoint with `?force=true`).
4. Nav entries for the two new pages; types added to `src/types/api.ts`; react-query keys per existing `query-keys` convention.
Gate: `pnpm type-check && pnpm build` clean; manual smoke instructions in report (backend running).

## Task 4: Cascade-matrix + restricted-delete tests (API level, `tests/test_integrity.py` new file)
Build fixture graph per test via API calls (register user(s), admin token, create category→skill(+prereq,resource,assessment,role mapping)→generate path→complete step→submit assessment), then assert EXACTLY the ERD contract from `src/migrations/003_reduced_schema.sql`:
1. DELETE skill (no deps) → 200; with deps → 409 body lists all six counters; `?force=true` → 200 and: skill_prerequisites gone, job_role_skills gone, user_skills gone, resources.skill_id NULL, assessments.skill_id NULL (questions kept), path_steps.skill_id NULL.
2. DELETE user → 200 forced-by-design (no restrict): paths/path_steps/step_progress/user_skills/assessment_results gone; activity_log.user_id NULL.
3. DELETE assessment → 200: questions gone, results gone (also covers previously-untested endpoint + 404 case).
4. DELETE path → 200: steps gone, step_progress gone (success-path delete finally covered).
5. DELETE category (no skills) → 200; with skills → 409 counting skills; `?force=true` → 200 and skills.category_id NULL; child categories' parent_id NULL.
6. DELETE job_role → mappings cascade; with mappings → 409 unless force.
7. Unique-violation behavioral inserts: dup category name, dup job_role title → 409 (not 500).
8. step_progress PK idempotency: double complete-step → still one row, 200 both times.

## Task 5: Negative-integrity + endpoint-gap tests
Extend existing files (auth/catalog/learning/assessments/admin/realtime) — no new file needed except where natural:
1. Auth: lockout — 5 wrong passwords → 429; correct login afterwards still 429 within window (read auth_service for window/reset semantics first; assert actual implemented behavior).
2. Assessments submit depth: partial score → proportional proficiency + passed=False below pass_score; boundary score == pass_score → passed=True; `assessment_results` row persisted (query via admin db-inspector or direct db_session fixture); resubmit upserts (no dup user_skills row, last_assessed_at updated); empty-questions assessment → 400.
3. Endpoint gaps: `GET /api/admin/assessments` shape/status asserted directly; `POST /api/admin/backups` → success key present (temp-dir safe); `GET /api/assessments/role/Frontend Developer` → non-empty list, correct item keys; unknown role → []; `POST /api/learning/generate` alias ≡ `/api/generate-path/` (same payload → 200 + path id); `GET /realtime/admin/events` + `/api/events` without token → 401/403 per existing gate style.
4. Ownership: complete/update/delete another user's path/step → 404; wizard mastery exclusion: user with proficiency ≥3 on a mapped skill → generated path omits it.
5. Path generation ordering: returned steps respect prerequisite topological order (assert every step's prerequisites appear earlier).

## Task 6: Code & content cleanup (delete dead/duplicate/stale)
1. Backend: remove `send_admin_event()` from `events/publisher.py`; strip dead re-export blocks in `dto/__init__.py`, `config/__init__.py`, `middlewares/__init__.py`, `events/__init__.py` (keep package docstrings + genuinely-imported names only; grep-verify each name before removing).
2. Delete `src/data/` entirely (orphaned legacy engine; verified zero importers).
3. Frontend: delete `src/frontend/src/i18n/hooks.ts` + `request.ts`; prune `useSSE.ts` DEFAULT_HANDLERS/query-invalidation entries for event types backend never emits (keep `connected`,`ping`,`path_generated`,`assessment_completed`); remove orphaned i18n keys (`notifications`, `streak`, `xp`, `achievements`) from BOTH ar.json+en.json preserving parity; re-run parity check.
4. Root: delete `seed_v2.py`, `src/seed/`, `src/migrations/001_aeis_initial_schema.sql 001_final_schema.sql 001_final_schema_v2.sql 002_rebuild_schema.sql`, `tools/audit_architecture.py db_reduction.py recovery_verification.py`, dirs `CERTIFICATION/ PHASE_A/ PHASE_B/ reports/archive/ reports/rediscovery/`, file `reports/qa-gate-final.md` (if still present).
5. `Dockerfile`: drop `COPY src/seed` line; ensure image builds conceptually (no docker build required — report notes it).
Gate: grep proves zero references to every deleted symbol/file; FULL suite green; SCHEMA MATCH; both builds green; parity equal.

## Task 7: Docs rewrite A — numbered SS-EDS sections (00–25 group)
Rewrite INDEX.md (and section .md files where they carry stale claims) of: `00-principles`(drop synth metaphor→Linear/Notion language), `01-product`, `02-business`(deployment: FastAPI+Next.js, SQLite/PostgreSQL — no Supabase/Render/Vercel claims), `03-functional-requirements`(junction tables = skill_prerequisites, job_role_skills; drop path_skills/skill_categories; roles→is_admin), `05-domain`(no streaks/gamification), `06-architecture`(15 tables, 8 layers, 7 routers, removed-layers list, no require_permission), `07-backend`(91→actual file counts, no validators/mappers/cache, JWT-only no refresh rotation, SSE no WebSocket), `08-frontend`(structure: app/,shared/,i18n/,types/ — NO entities/; no useWebSocket/XP), `09-admin`(is_admin binary; separate admin-app :3001), `10-database`(remove Alembic/Supabase lines; migrations = canonical DDL + verifier), `12-realtime`(SSE only, event types actually emitted, no notify/broadcast), `14-security`(JWT access-only, lockout, CSRF prod-only, CSP/HSTS, rate-limit, activity_log audit; no refresh/RBAC/profiles/roles tables), `15-performance`(inline TTL cache on public/stats + compression — no @cached/Redis), `16-testing`(pytest suite reality: files+counts, conftest isolation), `17-deployment`(run.py/uvicorn, Docker files present, env vars real ones), `21-accessibility`(Linear/Notion tokens; drop knob/cable/jack/--brass), `22-api`(46 paths/56 ops table per router incl. new Task-2 endpoints; tokens 30-min access, no refresh), `23-events`(SSE payloads actually emitted), `24-caching`(30s inline TTL; cache layer removed), `25-cli`(seed_v3.py, tools/verify_schema.py — no seed_all/src/scripts).
Each rewritten INDEX: ≤120 lines, states current truth with file/command references, zero stale signals (29/32 tables, alembic, RBAC roles, supabase, seed_all/seed_v2, WebSocket, streak/XP/achievement, synth metaphor, @cached, refresh-token).

## Task 8: Docs rewrite B — sections 26–50 + deletions
Rewrite INDEX of: `26-resource-engine`(resources.json via seed_v3; counts from live DB), `27-analytics`(dashboard keys real: mastered_skills, learning_velocity; no XP/level/streak), `28-gamification`→DELETE directory entirely (feature removed), `29-roadmaps`(current-state roadmap only), `30-images`(favicon.svg; drop synth icon list), `32-user-profile`(full_name only + skill_profile JSON from user_skills; no streak columns), `33-admin-profile`(is_admin binary; single admin class), `34-error-handling`(real handlers: 404/409/400 semantics, IntegrityError→409, error boundaries), `39-future`, `40-diagrams`(ERD already good; fix /ws line→SSE; sequence diagrams referencing removed flows pruned), `42-runbooks`(seed/verify/test/boot runbook with REAL commands), `44-test-scenarios`(scenarios matching actual suite), `45-release-notes`(add 2026-08 entry: 15-table reduction + CRUD completion + integrity layer), `46-glossary`(define current terms only; AEIS/synthesizer entries removed), `49-module-boundaries`(current layers+routers; crud/models/schemas gone), `50-anti-patterns`(keep principles; fix junction-table example to real tables; drop Phase-11 narrative).
DELETE entirely: `docs/pi-eos-mandatory/` (all 40 files), loose stale docs: `ADMIN_LAB_SPEC.md API.md ARCHITECTURE.md AUTH.md BACKEND.md DATA.md DEPLOYMENT.md DESIGN_SYSTEM.md FRONTEND.md LAYOUT_NAVIGATION.md LEARNER_EXPERIENCE.md MANAGER_STUDIO.md MICRO_UX_PHYSICS.md RESPONSIVE_DESIGN.md SERVICES.md TESTING.md`.
In `docs/41-decision-records/`: mark adr-007/adr-011 Superseded-by-adr-013; DELETE the five overlapping inventory reports (`backend_architecture_report.md large_files_report.md unused_files_report.md deleted_files_report.md dependency_audit.md runtime_root_cause.md` — six files total if runtime_root_cause present); update `41-decision-records/INDEX.md`.

## Task 9: Root docs + master INDEX + ADR-014
1. New `docs/41-decision-records/adr-014.md`: Referential-Integrity Policy — restrict+force delete rationale, FK validation, cycle guards, rename-uniqueness, IntegrityError→409 mapping; status Accepted.
2. Rewrite `docs/INDEX.md`: accurate TOC (dirs that exist post-prune), current quick-start (real commands), tech-stack line (FastAPI/SQLAlchemy/Next.js/pnpm/SQLite-PostgreSQL), API summary (7 routers/counts), no RBAC/Supabase/synth mentions; drop "Existing Files Mapped to New Structure" appendix (files being deleted).
3. Root `README.md` + `AGENTS.md`: reflect final counts (tables 15, routers 7, ops/paths actual post-Task-2, tests actual), new endpoints (categories/job-roles CRUD, PUTs), integrity policy one-liner, updated verification numbers; AGENTS.md keeps its format/table style.
4. `CONTRIBUTING.md`: verify commands match reality; minimal touch otherwise.
Gate: `grep -riE "supabase|alembic|seed_all|seed_v2|websocket|rbac|synthesizer|mastery-path|@cached" docs/ README.md AGENTS.md CONTRIBUTING.md` → zero hits (excluding adr historical records marked Superseded + intentional "removed" notes — reviewer judges).

## Task 10: FINAL GATE — CONTROLLER
Whole-branch review (most capable model) → ONE fix wave → scoped re-review. Then: seed ×2, SCHEMA MATCH, full pytest ×2, dev-DB rowcount unchanged, boot, live CRUD smoke (create→read→update→delete + restrict→force for skill/category/job_role), both builds, lint/type-check, i18n parity, QA report `reports/qa-gate-final-clean.md`.
