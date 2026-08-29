# SkillSynth: Rate Ladder Proficiency + Bank-First Step Tests + Admin Evaluations CRUD + Live Admin Tables — Implementation Plan

Goal: 
1. Turn the read-only per-step level ladder into an interactive "Rate" control (sets user_skills proficiency + step current_level).
2. Make step tests instant by switching to bank-first-by-default (AI as opt-in async enrich), mirroring the practice-test architecture.
3. Add full admin CRUD for evaluations (assessments + questions).
4. Make admin /paths and /audit-logs live (correct endpoint, SSE/refresh).

Confirmed decisions:
- Task 1 targets the per-step level ladder only (click a dot to set proficiency 0..5). No separate top-of-page control.
- Task 2 makes step quizzes bank-first by default (instant, deterministic); AI topic/quiz generation becomes opt-in enrich via SSE.

Tech Stack: Python/FastAPI/SQLAlchemy backend; SvelteKit (Svelte 5 runes) student app; SvelteKit admin app.

## Global Constraints
- Python imports: from backend import X (run.py injects src/ into PYTHONPATH).
- No function > 40 lines; every function carries a docstring (purpose + caller/callee).
- No file > 300 lines (seed_v3.py excepted). No comments unless requested.
- Bilingual AR/EN, RTL-first; 0 hardcoded frontend strings (use i18n).
- 15-table strict-3NF DB. AI bounded autonomy (ADR-015): AI proficiency review only ±1 at high confidence, clamped 0..5, audited in activity_log + SSE proficiency_adjusted.
- Tests: pytest, isolated temp DB — PYTHONPATH=src python -m pytest tests/ -q.
- Student app: pnpm in src/frontend (pnpm check/build). Admin app: pnpm in src/admin-app (pnpm check/build).

---

## Task 1 — "Rate" (level-ladder) proficiency

Diagnosis: The ladder dots in learn/[id]/+page.svelte (≈ lines 215-232) render step.current_level || step.selected_level || 1 and are display-only. There is no write path: no endpoint/service/repo writes proficiency/selected_level after a path is generated.

### Backend
- New endpoint `PUT /api/learning/skills/{skill_id}/proficiency` body `{level: 0..5}` bound to current user, in `src/backend/routers/learning.py`.
  - Validate `0 <= level <= 5` (400), skill exists (400) via `catalog_repository.get_skill`.
  - `arepo.upsert_user_skill(db, current_user.id, skill_id, level)` + `db.commit()` (assess_repository.py:122; caller commits — does not commit itself).
  - Update step(s) for that skill via a repo helper so the ladder reflects it: either reuse/extend `update_step_current_level` or add `update_step_current_level_for_skill(db, skill_id, level)` in learning_repository (set `current_level` on all PathStep rows of that skill).
  - Write activity log audit row via `engagement_repository.write(db, "learning", "rate.proficiency.set", user_id=current_user.id, entity_type="skill", entity_id=skill_id, data={"level": level})`.
  - Return the updated step(s)/success payload.
- DTO: add `RateProficiencyIn` (level: int ge=0 le=5) to `src/backend/dto/learning.py` (or catalog).
- Follow learning.py router style (current_user=Depends(get_current_user); raise HTTPException on error; no _fail pattern in this router).

### Frontend (student app)
- `src/frontend/src/routes/(app)/learn/[id]/+page.svelte`: make ladder dots clickable (`<button>` per dot) calling `apiFetch('/learning/skills/{step.skill_id}/proficiency', {method:'PUT', body:{level:n}})`; optimistically set `step.current_level = n`; then `invalidate(['path'])`/`load()`. Add `title`/tooltip label.
- i18n: add keys to both `src/frontend/src/lib/i18n/messages/en.json` + `ar.json` (learn section): `learn.rateLevel`, `learn.ratingSaved`, `learn.ratingFailed`.

### Tests (`tests/test_proficiency.py`, new)
- happy path: PUT valid level → user_skill.proficiency_level updated, step.current_level updated, 200.
- out-of-range 400 (level -1 and 6).
- unknown skill 400.
- activity_log row `rate.proficiency.set` written (query ActivityLog like test_ai_review.py).
- Use api_client/auth_headers/db_session fixtures; where rows accumulate, purge fixture mirrors test_ai_review.py.

---

## Task 2 — Step-test slowness (bank-first, AI async)

Diagnosis: step_test_service.py runs 4 synchronous local-LLM calls on the request path: `_leveled_topics`→`generate_skill_topics` on open, `_ai_questions`→`generate_skill_quiz` on open, `_persist_grade`→`review_level` on every submit, `_diagnostic_for_fail`→`analyze_diagnostic` on fail. This is the tens-of-seconds lag. Mirror the established `assess_service` architecture (answer-first + `_spawn_review`/`_queue_review`/`_review_and_adjust`).

### Backend (`src/backend/services/step_test_service.py`)
- `generate_step_test` (:201-227): make bank-first deterministic by default — use `_seeded_questions` synchronously; never call the LLM on the request path unless an explicit `enrich` flag is passed. AI topic/quiz generation becomes an opt-in background daemon thread that streams via SSE `ai_step_quiz_ready` (only when `enrich=true`). Default: instant, from the bank.
- `_grade`/`grade_step_test` (:349-381): grade deterministically & synchronously (`_score_answers` + `_persist_grade` math, no LLM) — complete the step on pass and return immediately (the deterministic `level = max(0, min(5, round(correct/total*scale)))` formula, not LLM review_level). The AI level-review + diagnostic narrative move off the request path: after committing, `_spawn_review` a bounded review that (a) applies audited ±1 proficiency_adjusted adjustment (ADR-015 bounded autonomy + activity_log + SSE `proficiency_adjusted`), (b) emits `ai_step_diagnostic` SSE carrying refined weak_points/topics_to_master, applied by the frontend to the already-shown result.
- Introduce seams mirroring assess_service: `_spawn(fn)` daemon-thread seam and `_engine_ready()` gate; each background job opens its own `SessionLocal()` and closes in finally; lazy `from backend.events.publisher import send_event`.
- Keep helper behavior/deterministic math; `question_bank`/`_seeded_questions` remain the bank source.

### Frontend (student app)
- `learn/[id]/+page.svelte` + `QuizRunner.svelte`: results render instantly from the sync submit response. Add SSE listener for `ai_step_diagnostic` to upgrade the shown weak_points/topics_to_master when the AI narrative arrives; add listener for `proficiency_adjusted` to refresh the ladder. Add optional "enrich" affordance only if we keep AI-generated step quizzes opt-in (optional).
- `src/frontend/src/lib/stores/sse.ts`: register `ai_step_diagnostic` (and any new event names) in the frame-type list and dispatch as `sse:<type>`.
- No answer-mapping changes (grading stays aligned).

### Tests
- Update `tests/test_step_test.py` / `test_step_test_api.py` assertions that expect synchronous LLM enrichment: patch `_spawn*` to run inline and `llm_pipeline._engine_available → False` (matching existing patterns).
- New tests: step-test open is deterministic/bank-sourced & fast (no LLM on request path); submit grades synchronously without blocking AI; AI diagnostic arrives via the background path (patch spawn inline + assert SSE event + audit row).
- Full suite must stay green.

---

## Task 3 — Admin full CRUD for evaluations (assessments + questions)

Diagnosis: Backend has only GET /admin/assessments (list) + DELETE with force (admin.py:92-112; missing skill_name/question_count; restricted-delete census guarded). Frontend admin assessments page is list + delete only. assess_repository has create_assessment_with_questions (line 135).

### Backend
- New router `src/backend/routers/evaluations_admin.py` mounted under `/api/admin` (main.py: import + include_router after catalog_admin), admin-gated via router-level `APIRouter(dependencies=[Depends(require_admin)])`, following catalog_admin.py's `(result, error)` + `_fail`/`_fail_create` + `status_for_error` pattern. Every function has a docstring.
  - `GET /admin/assessments` (exists in admin.py — move/extend to include `skill_name` + `question_count`). Preserve the exact existing list key contract referenced by tests (test_admin.py:143-154 asserts `{id, skill_id, title, assessment_type, passing_score}`) — extend additively, do not remove keys, or update that test.
  - `GET /admin/assessments/{id}` — metadata + ordered questions.
  - `POST /admin/assessments` (skill_id, title, description, pass_score) → 400 unknown skill.
  - `PUT /admin/assessments/{id}` — metadata; 404 missing / 400 unknown skill.
  - `DELETE /admin/assessments/{id}?force=` (keep existing restricted-delete flow).
  - Questions sub-resource:
    - `POST /admin/assessments/{id}/questions` — add (position=next+1); validate options ≥2 entries, 0<=correct_index<len(options).
    - `PUT /admin/assessments/{id}/questions/{qid}` — update prompt/options/correct_index/position (same validation; on position change re-slot neighbors).
    - `DELETE /admin/assessments/{id}/questions/{qid}` — delete, reindex positions; require ≥1 question remains (400 if last).
- Service `src/backend/services/evaluations_service.py`: reusable `(result, error)` functions calling new `assess_repository` helpers (`create_assessment`, `update_assessment`, `get_assessment_detail`, `add_question`, `update_question`, `delete_question`, `reorder_questions`) plus existing `create_assessment_with_questions`/`delete_assessment`.
- Repository `assess_repository.py`: add the write helpers above (commit + refresh pattern like catalog_repository). skill FK validated → 400; assessment_question.assessment_id CASCADE is model-level safety during force-delete; options JSON documented exception maintained.
- DTOs: add evaluator request/response models to `src/backend/dto/admin.py` (AssessmentCreate/Update, QuestionCreate/Update, AssessmentDetailOut) following dto/catalog.py validation patterns (sanitizer, field constraints).

### Frontend (admin app)
- Rebuild `src/admin-app/src/routes/(app)/assessments/+page.svelte` to full CRUD mirroring skills/+page.svelte pattern: toolbar Add, list with skill name / type / pass score / question count, Edit + Delete (force) dialogs, questions detail dialog with inline question table (position, prompt, options, correct_index) supporting add/edit/delete/reorder. Keep restricted-delete 409-with-dependents force flow.
- Add skill options fetch `/admin/skills` for the create/edit form select.
- i18n: add keys to both `src/admin-app/src/lib/i18n/messages/en.json` + `ar.json` under `admin.assessments`.
- sse.ts already invalidates ['ASMT'] on assessment_completed — list stays live.
- `src/admin-app/src/lib/types/api.ts`: extend Assessment interface with skill_id/description/questions.

### Tests
- Add backend tests for the evaluations endpoints: create/update/delete assessment, question add/update/delete/reorder, unknown skill 400, position re-slotting, last-question-delete 400, validation 400s. Mirror existing admin route test style in tests/.

---

## Task 4 — Static admin /paths and /audit-logs

### /paths (`src/admin-app/src/routes/(app)/paths/+page.svelte`)
- Currently fetches `/paths` (per-user, wrong for admin) and never refreshes. Switch to `/admin/paths` (returns PathAdminView rows with user_email/is_completed that the table already renders — no schema change).
- Add Refresh button; add `$effect` listener for `sse:path_generated` DOM event (dispatched by sse.ts) that calls `invalidate(['PATHS']); await load()`.

### /audit-logs (`src/admin-app/src/routes/(app)/audit-logs/+page.svelte`)
- Keep the live `sse:activity` prepend; add (a) periodic re-fetch (e.g. every 30s via setInterval with cleanup) so full history reconciles, (b) manual Refresh button. Replaces the once-only snapshot with a live-updating feed.

### Backend admin SSE publish (user-confirmed scope addition)
The backend currently never publishes to the admin SSE channel, so `sse:path_generated`/`sse:activity` are dead in the admin app. Add:
- `src/backend/events/publisher.py`: add `send_admin_event(event_type, data=None)` that enqueues `{"type": event_type, **data}` to every queue in `admin_event_clients` (QueueFull swallowed, mirroring `send_event`).
- Broadcast to the admin channel (in addition to the per-user channel) from:
  - `routers/paths.py:41` (`path_generated`) → `send_admin_event("path_generated", {"path_id": ...})` (and optionally the full PathAdminView row so /paths can refresh).
  - `routers/assessments.py:117` (`assessment_completed`) → `send_admin_event(...)` so the admin list invalidates (already invalidated via sse.ts ASMT).
  - Activity log writes: emit an `activity` admin frame whenever `engagement_repository.write` produces a row (so /audit-logs `sse:activity` prepend is genuinely live). Insert a broadcast call next to existing `write()` call sites (or in `write` itself — prefer a small explicit helper call at the audit call sites to keep the repo dependency-free, then re-emit `send_admin_event("activity", {...row})`).
- Keep per-user `send_event` behavior unchanged (regression: RT /admin/events tests unaffected).

These make /paths + /audit-logs genuinely live; the frontend sse listeners then fire.

---

## Verification
- Backend: `PYTHONPATH=src python -m pytest tests/ -q` — full suite green (199 tests baseline; note unrelated pre-existing test_stable_catalog_counts 152-vs-155 skills failure to be flagged separately).
- Student app: `cd src/frontend && pnpm check && pnpm build`.
- Admin app: `cd src/admin-app && pnpm check && pnpm build`.
- Schema: `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH (no schema change expected).
