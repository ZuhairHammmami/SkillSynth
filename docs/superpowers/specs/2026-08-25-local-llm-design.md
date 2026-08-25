# SS-AI — Local LLM Integration Design

**Date:** 2026-08-25 · **Status:** Approved (user-reviewed in session) · **ADR:** 015 · **Branch:** feature/smart-mentor-v1

## Purpose

Integrate a locally-hosted Llama-3.2-3B-Instruct GGUF model as an integral SkillSynth subsystem that:

1. Generates adaptive MCQ quizzes/tests (wizard diagnostic + single-skill practice tests).
2. Produces detailed result presentations — per-skill scores, flagged weaknesses, narratives — **before** a learning path is created (two-phase wizard).
3. Explains completed test results per question with study advice.
4. Applies **bounded** proficiency-level adjustments (±1 max, high-confidence only, fully audited).

The deterministic engine remains the source of truth: scoring (`_grade`), the proficiency formula (`round(correct/total × 5)` clamp 0–5), prerequisite topological sort, and path persistence are unchanged code paths. The LLM augments; it never grades numerically except through the clamped review delta.

## Runtime Decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Serving | In-process `llama-cpp-python` | Consumes exact GGUF path; no extra service; simplest deployment |
| Model | **User-provided file** at `src/data/Llama-3.2-3B-Instruct-uncensored.Q6_K.gguf` (2,967,059,008 B; header metadata: `Meta Llama · Llama 3.2 3B Instruct`, no abliteration markers). **Ruling (user, session):** reuse this existing artifact instead of downloading a verified-standard copy — filename kept as-is for provenance honesty. | Standard-model behavior per embedded metadata; filename legacy documented |
| Hardware | NVIDIA GTX 1650 Ti 4 GB → CUDA offload `AI_N_GPU_LAYERS=-1` | ~50–100 tok/s generation; sync analyses viable |
| Timing | Generation endpoints async+SSE; analysis/explanations sync | Long outputs vs GPU-fast short outputs |
| Persistence | Wizard AI quiz ephemeral (matches current wizard semantics); standalone practice tests persist as real `[AI] <Skill>` assessments | Fits existing single-skill `assessments` FK model; results/analytics/reports flow unchanged |
| Feature gate | `AI_ENABLED` **default false** | All 143 existing tests byte-identical green without model; graceful degradation everywhere |

## Architecture

Zero schema changes — the 15-table DDL stays frozen. New flat modules following existing conventions (<300 lines/file, <40-line functions with purpose/caller-callee docstrings, `from backend import X`):

```
src/backend/services/
├── llm_engine.py    lazy singleton GGUF loader; semaphore-serialized inference;
│                    warmup(); health(); startup existence guard (clear log, degrade)
├── llm_prompts.py   strict JSON-contract templates: quiz_gen · diagnostic_analysis ·
│                    explain_result · level_review (system prompt pins examiner role)
└── llm_pipeline.py  four ops with JSON validation (1 retry on parse failure) and
│                    graceful fallbacks; quiz validation: exactly 4 options,
│                    correct_index in range, dedupe vs seed pool, shortfall filled from seed
```

New thin router `routers/ai.py`. Repositories/entities untouched. Background jobs use an in-memory registry consistent with the existing SSE pub/sub pattern (`events/publisher.py`). Inference serialized by semaphore (single concurrent completion).

## API Surface (+4 ops, +4 paths → 67 ops / 53 paths)

| Endpoint | Mode | Behavior |
|---|---|---|
| `POST /api/ai/wizard-quiz` `{goal}` | async → SSE `ai_quiz_ready` | Adaptive MCQs across goal-role skills keyed to the load-bearing `<skill>_q<i>` contract; ephemeral |
| `POST /api/wizard/analysis` `{goal, answers}` | sync | Phase-1 report: per-skill score/level/gap, weaknesses flagged+explained, strengths, focus areas (LLM narrative when enabled). Pure recompute reusing `_score_answers`; **persists nothing** |
| `POST /api/ai/tests/generate` `{skill_id}` | async → SSE `ai_test_ready {assessment_id}` | Weakness-targeting practice test persisted as `[AI] <Skill> — adaptive` assessment; graded by existing `_grade` |
| `POST /api/ai/explain` `{assessment_id, answers}` | sync | Per-question explanations + study advice. **Amendment:** the originally sketched `GET /api/ai/results/{id}/explanation` is impossible without schema changes — `assessment_results` stores score/passed only, never the selected indices. Grading inputs are therefore re-supplied in-body and graded in-memory (zero writes). |

Post-submit hook (internal, async): bounded level review → SSE `proficiency_adjusted {delta, rationale}`.

## Bounded-Autonomy Policy

`review_level()` input: response detail (selected vs correct texts), difficulty, attempt count, current level. Output contract (temperature ≤0.2):

```json
{"suggested_delta": -1|0|1, "confidence": "high|medium|low", "rationale": "<=300 chars"}
```

Applied **only if** confidence == high; final = `clamp(formula_level + delta, 0, 5)`; every application audited in `activity_log.data` (existing documented JSON exception) with type `ai_proficiency_review`. Rationale strings surface in admin events feed/reports — thesis evidence trail.

## Config & Dependency Hygiene

- `.env` adds: `AI_ENABLED`, `AI_MODEL_PATH=src/data/Llama-3.2-3B-Instruct.Q6_K.gguf`, `AI_N_GPU_LAYERS=-1`, `AI_N_CTX=4096` (tunable down on VRAM pressure), `AI_TEMPERATURE=0.2`, `AI_MAX_NEW_TOKENS`.
- Removes dead legacy blocks: `OLLAMA_*`, `OPENAI_*`, `TRACK_LLM_COSTS`, `DEBUG_LLM_PROVIDER`, vector/embedding vars; docker-compose optional ollama service dropped.
- `requirements.txt`: removes `openai`, `langchain*`, `ollama`; adds `llama-cpp-python>=0.3` with documented CUDA install (`CMAKE_ARGS="-DGGML_CUDA=on"`) and CPU fallback (`AI_N_GPU_LAYERS=0`).
- Known risks: Python 3.14 wheel availability (source-build fallback), 4 GB VRAM budget for 2.76 GB weights + KV cache (partial offload documented as remedy).

## Failure Handling

Model missing / load fail / invalid JSON after retry → log + fall back: wizard-quiz → seeded question pool; analysis narrative → deterministic-only report (flagged `narrative_available:false`); practice-test generation → clear error suggesting seeded quizzes; explanation → static correct-answer recap (already computed by `_grade`); review → delta 0. `AI_ENABLED=false` short-circuits all new endpoints cleanly.

## Frontend (student app; ar/en i18n parity, RTL-safe)

Wizard resteps: Goal → “Generate adaptive quiz” (SSE progress) → Quiz (dynamic questions, existing answer UI) → **new Results Review page** (breakdown cards, weaknesses explained, narrative) → Confirm → `generate-path` (unchanged call). Plus: weaknesses-panel “Practice test” button, result-page “Explain results” section, subtle “level adjusted” notice. Admin app: flags page shows real `ai_features` (read-only display only).

## Documentation Wave (thesis-minimal)

ADR-015 (local-first rationale, runtime comparison vs Ollama/API, bounded-autonomy policy, ephemeral-vs-persisted quiz policy) · one new SS-EDS section (standard template) · amend `05-domain` “no LLM in the loop”, root `docs/INDEX.md`, `.env.example`, `AGENTS.md` (67 ops/53 paths), ERD “schema unchanged” note.

## Verification Battery (release gate)

```
PYTHONPATH=src python -m pytest tests/ -q        # 143 existing + ~30 new (fake engine, isolated DB)
PYTHONPATH=src python tools/verify_schema.py     # SCHEMA MATCH
cd src/frontend && pnpm type-check && pnpm lint && pnpm build
cd src/admin-app && pnpm type-check && pnpm build
PYTHONPATH=src python run.py                     # boot with AI_ENABLED=false and true
```

Slow real-model smoke test is marked and auto-skipped when the GGUF file is absent.
