# SS-EDS: AI Integration

## Purpose
Document the SS-AI local-LLM subsystem (ADR-015, hardened by ADR-016, sped up by ADR-017): five endpoints served by an in-process llama-cpp-python GGUF runtime (`services/llm_engine.py`, `llm_pipeline.py`, `llm_prompts.py`, `llm_validation.py`, `llm_batching.py`) with GPU offload, grounded in the project catalog via `services/knowledge_layer.py` (no fine-tuning), the bounded-autonomy proficiency policy, the degradation ladder, and batched/token-trimmed/async-narrative speed work. The deterministic engine remains the source of truth; the LLM augments.

## Responsibilities
- Generate adaptive MCQ quizzes (wizard diagnostic) and single-skill practice tests
- Present detailed results + weaknesses BEFORE path creation (two-phase wizard, zero-write analysis)
- Explain completed results per question with study advice
- Apply bounded, audited post-submit proficiency review (−1/0/+1)
- Degrade gracefully when AI is disabled or the model is unusable

## Inputs
- Wizard goal/preferences and submitted answers (POST /api/wizard/analysis)
- Skill ids for quiz/test generation (POST /api/ai/wizard-quiz, POST /api/ai/tests/generate)
- Submitted answer sets for explanation (POST /api/ai/explain)
- Model file: `src/data/Llama-3.2-3B-Instruct-Q6_K.gguf` (2,643,853,856 B (~2.46 GiB); header metadata = standard Meta Llama 3.2 3B Instruct, no abliteration markers; filename kept for provenance)

## Outputs
- Quiz/test question sets delivered via SSE job events
- Diagnostic report (per-skill scores, weaknesses, narrative) — narrative streams in asynchronously via `narrative_ready` SSE (ADR-017); `narrative_available:false` until it arrives or when degraded
- Persisted `[AI] <Skill> — adaptive` assessments (practice tests only)
- `activity_log(action='ai_proficiency_review')` rows + `proficiency_adjusted` SSE frames

## Dependencies
- 07-backend (routers/ai.py, learning.py, paths.py · llm_engine/llm_pipeline/llm_prompts/llm_validation/llm_batching · knowledge_layer)
- 11-learning-engine (deterministic scoring/topo-sort — unchanged code paths)
- 12-realtime / 23-events (SSE transport + new event types)
- 41-decision-records/adr-015 (decision record) + adr-016 (grounding + GPU runtime fix) + adr-017 (AI speed: batching, token trim, async narrative)

## Sequence: Two-Phase Wizard
```
Goal → POST /api/ai/wizard-quiz → jobId → SSE ai_quiz_ready|ai_quiz_failed (batched completions, ADR-017)
    → answers → POST /api/wizard/analysis (PURE — zero writes; INSTANT, narrative via SSE narrative_ready)
    → ResultsStep (scores · weaknesses · narrative when it arrives) → CTA → Summary
    → POST /api/generate-path/ (deterministic generation, unchanged)
```

## Endpoints (5)
| Method & Path | Writes? | Notes |
|---------------|---------|-------|
| POST /api/ai/wizard-quiz | none | ephemeral quiz job → SSE delivery |
| POST /api/ai/tests/generate | assessments row | persists `[AI] <Skill> — adaptive` practice test |
| POST /api/wizard/analysis | none | PURE two-phase analysis before path creation |
| POST /api/ai/explain | none | per-question why + study advice; falls back `narrative_available:false` |
| GET /api/learning/analysis | none | weaknesses/diagnostic feed for analytics panel |

All gated by the runtime AI flag → **503** `{"detail":"AI features are disabled"}` when off; all require Bearer auth. The flag defaults from the `AI_ENABLED` env var and is **overridable at runtime** via the admin `PUT /api/admin/feature-flags` endpoint (persisted to `src/data/settings.json`), so an admin can enable/disable AI from the UI without restarting.

## Emitted Event Types (6 new — verified in code)
| Event | Source | Payload |
|-------|--------|---------|
| ai_quiz_ready | routers/ai.py | {"job_id", "questions", ...} |
| ai_quiz_failed | routers/ai.py | {"job_id", "error"} |
| ai_test_ready | routers/ai.py | {"job_id", "assessment_id", ...} |
| ai_test_failed | routers/ai.py | {"job_id", "error"} |
| proficiency_adjusted | services/assess_service.py | {"skill_id", "delta", ...} |
| narrative_ready | routers/paths.py | {"analysis_id", "narrative"} — async wizard narrative (ADR-017) |

Existing `assessment_completed` / `path_generated` frames are unchanged.

## Rules
1. **Ephemeral vs persisted**: wizard AI quizzes are EPHEMERAL (SSE-only); standalone practice tests PERSIST as assessments titled `[AI] <Skill> — adaptive`
2. **Bounded autonomy**: review may adjust proficiency −1/0/+1 ONLY at confidence==high, clamped to 0..5; audited in activity_log + SSE; deterministic formula never overwritten
3. Config vars: `AI_ENABLED(false)` · `AI_MODEL_PATH` · `AI_N_GPU_LAYERS(-1)` · `AI_N_CTX(4096)` · `AI_TEMPERATURE(0.3)` · `AI_REPEAT_PENALTY(1.15)` · `AI_TOP_P(0.95)` · `AI_MAX_NEW_TOKENS(700)` · `AI_GRAMMAR(false)`
4. Runtime: llama-cpp-python 0.3.x in-process. The installed build is **CUDA-capable**; CUDA 13.3 lives at `/opt/cuda`, and `skillsynth run`/`doctor` place `/opt/cuda/lib64` on `LD_LIBRARY_PATH` so the backend loads in-process with GPU offload. `_fit_layers` auto-caps `gpu_layers` to fit the card (26 of 28 for the 3B Q6_K), degrading to CPU only when VRAM is occupied. A fresh CUDA rebuild is still supported:
   ```bash
   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
   ```
5. Python 3.14 has no prebuilt wheel yet — source-build fallback expected
6. **Grounding (ADR-016)**: prompts are grounded in the real catalog via `services/knowledge_layer.py` (`skill_context`, `knowledge_digest`), invalidated on catalog writes; `AI_GRAMMAR=true` opts into constrained GBNF grammar sampling for structurally-valid JSON
7. **Speed (ADR-017)**: role quizzes batch skills (groups of 4, one completion per batch; all-empty → split-half retry → per-skill fallback); `max_tokens` ceilings are trimmed (`min(700, max(180, n*95))` skills · 400 analysis · 500 explain); `/api/wizard/analysis` returns instantly and emits the narrative asynchronously via `narrative_ready` SSE

## Failure Cases (degradation ladder)
- `AI_ENABLED=false` → 503 gate on every AI endpoint
- Model missing/corrupt → `LLMUnavailable` latch in llm_engine
- Quiz ops under latch → raise → SSE `ai_quiz_failed` / `ai_test_failed`
- analysis/explain under latch → deterministic-only response with `narrative_available:false`
- Review under latch → delta 0 (no write, no audit row)

## Examples
- Practice test: POST /api/ai/tests/generate → assessment row `[AI] Python — adaptive` → submit flows through existing /api/assessments/submit → analytics unchanged
- Review: high-confidence model suggests +1 on level 4 → user_skills.proficiency_level 5, activity_log row, `proficiency_adjusted` frame

## Edge Cases
- Suggested +1 at level 5 → clamp holds (applied=false, final=5), reported delta keeps suggestion
- Low-confidence review or engine exception → delta 0, rationale recorded
- Model output malformed (non-MCQ, out-of-range indices) → sanitized/stripped by pipeline guards

## Recovery Procedures
1. 503 responses → set `AI_ENABLED=true`, verify model path exists, restart
2. `LLMUnavailable` after corrupt download → re-acquire the GGUF, clear the latch via restart
3. Missed SSE frames → refetch `/api/learning/analysis`; failed jobs may be re-requested

## Refactoring Strategy
- Engine swaps (bigger quant, different backend) stay behind llm_engine's single interface — ADR required for provider changes only
- New AI endpoints must extend this section and docs/22-api together
