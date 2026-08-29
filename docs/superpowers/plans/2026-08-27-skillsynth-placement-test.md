# SkillSynth: Placement Test + AI Activation — Implementation Plan

Goal: Make path creation include a working placement step (AI quiz when AI is enabled, deterministic self-assessment fallback) that persists per-skill proficiency and shapes the generated path, and unify the AI flag so the admin-panel toggle is the single runtime source of truth and takes effect immediately.

Architecture: The backend already contains both paths — self-report slider → POST /api/wizard/analysis, and AI quiz → POST /api/ai/wizard-quiz + quiz_job_id grading in routers/paths.py. The defects are: (a) self-report keys are mis-shaped so levels never persist; (b) the AI flag is read from two sources (app_settings.AI_ENABLED env constant vs settings_service.is_ai_enabled() runtime store) so the admin toggle doesn't drive path-creation AI; (c) the frontend never calls/renders the AI quiz nor shows real placement results. We fix the key mapping + persistence, repoint the two env-gated paths to the runtime store, and wire the wizard to run/display the AI quiz with a deterministic fallback.

Tech Stack: Python/FastAPI/SQLAlchemy backend; SvelteKit (Svelte 5 runes) student app; SvelteKit admin app.

## Global Constraints
- Python imports: from backend import X (run.py injects src/ into PYTHONPATH).
- No function > 40 lines; every function carries a docstring (purpose + caller/callee).
- No file > 300 lines (seed_v3.py excepted). No comments unless requested.
- Bilingual AR/EN, RTL-first; 0 hardcoded frontend strings (use i18n).
- 15-table strict-3NF DB. AI bounded autonomy (ADR-015): AI proficiency review only ±1 at high confidence, clamped 0..5.
- Tests: pytest, isolated temp DB — PYTHONPATH=src python -m pytest tests/ -q.

## Context / verified diagnosis
- Admin PUT /api/admin/feature-flags writes src/data/settings.json; settings_service.is_ai_enabled() reads it at request time.
- settings.json is currently seeded {"ai_enabled": true} but step_test_service/llm_pipeline consult the env constant (default false), so they stay off. Unifying on settings_service makes display == behavior.
- step_test_service.py:116 and llm_pipeline.py:169 are the two env-gated locations to repoint.
- learning_service.py _score_answers ~71-104; _persist_plan 152-165; generate_path 185-187.
- dto/learning.py:224 WizardAnalysisIn.quiz_job_id.

## Task 1: Unify AI flag to runtime settings store (backend)
Files:
- Modify: src/backend/services/step_test_service.py:116
- Modify: src/backend/services/llm_pipeline.py:169
- Test: tests/test_ai_flag_unification.py (new)
Interfaces:
- Consumes: settings_service.is_ai_enabled() -> bool (already runtime; reads settings.json).
- Produces: step-test AI + skill-topic generation now share the same source as routers/ai.py, llm_engine.py, assess_service.py, paths.py:242.
-   Step 1: Write failing test
```python
from backend.services import settings_service
def test_flag_drives_step_test_and_topics():
    settings_service.set_ai_enabled(False)
    # step-test gate + topic generation must be OFF
    assert not step_test_service._ai_step_test_enabled()   # helper gating line 116
    assert llm_pipeline._engine_available() is False or llm_pipeline.generate_skill_topics("X", 1) == FALLBACK
    settings_service.set_ai_enabled(True)
    assert step_test_service._ai_step_test_enabled() is True
```
- Step 2: Run test → FAIL (settings.AI_ENABLED env constant ignores toggle).
- Step 3: Implement — replace settings.AI_ENABLED with settings_service.is_ai_enabled() at both lines; add from backend.services import settings_service if missing.
- Step 4: Run test → PASS; run full suite (pytest tests/ -q) → no regression.
- Step 5: Commit.

## Task 2: Fix deterministic self-assessment persistence + path shaping
Files:
- Modify: src/backend/services/learning_service.py (_score_answers ~71-104; _persist_plan 152-165; generate_path 185-187)
- Test: tests/test_placement_selfassess.py (new)
Interfaces:
- Consumes: WizardAnalysisIn {goal, weekly_hours, answers: dict} from routers/paths.py.
- Produces: user_skills.proficiency_level + path_steps.selected_level/current_level set from self-report; generate_path excludes skills at/above MASTERY_LEVEL (3); analysis returns real weaknesses/focus.
-   Step 1: Write failing test
```python
def test_selfreport_shapes_path():
    # role skills A(5 mastered), B(2), C(0); answers={"A":5,"B":2,"C":0}
    result = learning_service.generate_path(user, role, answers={"A":5,"B":2,"C":0}, weekly_hours=10)
    names = {s.skill_id for s in result.steps}
    assert "A" not in names and "B" in names and "C" in names
    assert user.user_skills["A"].proficiency_level == 5
```
- Step 2: Run → FAIL (keys _q{i} never match → all level 0 → all included).
- Step 3: Implement — in _score_answers, for each skill: val = answers.get(skill.name); if isinstance(val,(int,float)) and 0<=val<=5 → level=val; elif <skill>_q<i> present → parse; else current. Return levels dict. In _persist_plan, use that computed levels for step.selected_level/current_level and user_skills.proficiency_level (not the never-sent data.levels). Confirm generate_path (185-187) skips skills whose reported level ≥ MASTERY_LEVEL.
- Step 4: Run test → PASS; full suite green.
- Step 5: Commit.

## Task 3: Frontend — send placement, show results, fix reverse indicator + analytics NaN
Files:
- Modify: src/frontend/src/routes/(app)/wizard/+page.svelte (payload + results rendering)
- Modify: src/frontend/src/routes/(app)/analytics/+page.svelte:80 (pass growth.skills, not whole response)
- Verify: src/frontend/src/lib/components/TopSkills.svelte (reads proficiency), learn/[id]/+page.svelte ladder (reads step.current_level)
- Verify/type: cd src/frontend && pnpm type-check && pnpm lint
Interfaces:
- Consumes: /api/wizard/analysis now returns real analysis (Task 2).
- Produces: wizard sends answers as {skillName: level}; renders placed levels + weakness/focus chips from real data; analytics bars use growth.skills proficiency.
-   Step 1: Confirm wizard submit payload sends answers = {skillName: sliderValue} (0-5) matching Task 2 shape.
-   Step 2: In the review/summary step, render each skill's placed level (from analysis response) and weakness/focus chips from real data (not placeholder zeros); wire returned report rows.
-   Step 3: Fix analytics/+page.svelte:80 to pass growth.skills (array) so it.proficiency*20 is numeric (fixes NaN bars).
-   Step 4: Confirm learn/[id] ladder uses step.current_level/selected_level (already correct) — now accurate because backend persists (Task 2). This resolves the "indicator works in reverse" report (it was showing the stale/zero fallback, not an inverted formula).
-   Step 5: pnpm type-check && pnpm lint → 0 errors.
-   Step 6: Commit (frontend).

## Task 4: Wire AI placement quiz into wizard (with fallback)
Files:
- Verify/Modify backend: src/backend/routers/ai.py (wizard-quiz ~94), src/backend/routers/paths.py (quiz_job_id grading 185-229), src/backend/dto/learning.py:224 (WizardAnalysisIn.quiz_job_id)
- Modify frontend: src/frontend/src/routes/(app)/wizard/+page.svelte (quiz flow) + src/frontend/src/lib/stores/sse.ts (already has ai_quiz_ready)
- Test backend: tests/test_ai_placement_quiz.py (mock llm_engine)
Interfaces:
- Consumes: settings_service.is_ai_enabled() (Task 1) for availability on both frontend (feature-flags/status) and backend gate.
- Produces: when AI enabled, wizard runs per-skill quiz, grades via quiz_job_id, returns per-skill proficiency + weak points + topics; when disabled, falls back to Task 2/3 self-assessment; results displayed.
-   Step 1: Backend test — with is_ai_enabled() True + mocked engine, POST /api/ai/wizard-quiz returns a job; grading via /wizard/analysis quiz_job_id yields per-skill levels + report. With False → 503 (already).
-   Step 2: Frontend — after skills/goal step, read AI availability (GET /api/admin/feature-flags → ai_enabled, or /api/ai/status). If enabled: "Take placement quiz" → POST /api/ai/wizard-quiz with selected skills → render streamed questions (use sse store ai_quiz_ready or poll job) → collect answers → POST /wizard/analysis with {goal, weekly_hours, quiz_job_id}. If disabled: skip to self-assessment slider (Task 2/3).
-   Step 3: Render quiz results — per-skill score, weak points, recommended topics/resources (from analysis report rows), using i18n keys (add bilingual keys if missing).
-   Step 4: Ensure deterministic fallback (Task 2/3) still works when AI off.
-   Step 5: pnpm type-check && pnpm lint; backend pytest tests/ -q.
-   Step 6: Manual e2e — AI toggle ON in admin → path creation shows placement quiz, results drive path; toggle OFF → self-assessment drives path.
-   Step 7: Commit.

## Execution Handoff
Plan complete. Options: 1. Subagent-Driven (recommended). 2. Inline Execution.
