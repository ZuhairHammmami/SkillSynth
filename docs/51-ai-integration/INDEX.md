# SS-EDS: AI Integration

## Purpose
Document the SS-AI local-LLM subsystem (ADR-015): five endpoints served by an in-process llama-cpp-python GGUF runtime (`services/llm_engine.py`, `llm_pipeline.py`, `llm_prompts.py`), the bounded-autonomy proficiency policy, and the degradation ladder. The deterministic engine remains the source of truth; the LLM augments.

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
- Model file: `src/data/Llama-3.2-3B-Instruct-uncensored.Q6_K.gguf` (2,967,059,008 B; header metadata = standard Meta Llama 3.2 3B Instruct, no abliteration markers; filename kept for provenance)

## Outputs
- Quiz/test question sets delivered via SSE job events
- Diagnostic report (per-skill scores, weaknesses, narrative) — `narrative_available:false` when degraded
- Persisted `[AI] <Skill> — adaptive` assessments (practice tests only)
- `activity_log(action='ai_proficiency_review')` rows + `proficiency_adjusted` SSE frames

## Dependencies
- 07-backend (routers/ai.py, learning.py, paths.py · llm_engine/llm_pipeline/llm_prompts)
- 11-learning-engine (deterministic scoring/topo-sort — unchanged code paths)
- 12-realtime / 23-events (SSE transport + new event types)
- 41-decision-records/adr-015 (decision record)

## Sequence: Two-Phase Wizard
```
Goal → POST /api/ai/wizard-quiz → jobId → SSE ai_quiz_ready|ai_quiz_failed
    → answers → POST /api/wizard/analysis (PURE — zero writes)
    → ResultsStep (scores · weaknesses · narrative) → CTA → Summary
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

All gated by `AI_ENABLED` → **503** `{"detail":"AI features are disabled"}` when off; all require Bearer auth.

## Emitted Event Types (5 new — verified in code)
| Event | Source | Payload |
|-------|--------|---------|
| ai_quiz_ready | routers/ai.py | {"job_id", "questions", ...} |
| ai_quiz_failed | routers/ai.py | {"job_id"} |
| ai_test_ready | routers/ai.py | {"job_id", "assessment_id", ...} |
| ai_test_failed | routers/ai.py | {"job_id"} |
| proficiency_adjusted | services/assess_service.py | {"skill_id", "delta", ...} |

Existing `assessment_completed` / `path_generated` frames are unchanged.

## Rules
1. **Ephemeral vs persisted**: wizard AI quizzes are EPHEMERAL (SSE-only); standalone practice tests PERSIST as assessments titled `[AI] <Skill> — adaptive`
2. **Bounded autonomy**: review may adjust proficiency −1/0/+1 ONLY at confidence==high, clamped to 0..5; audited in activity_log + SSE; deterministic formula never overwritten
3. Config vars: `AI_ENABLED(false)` · `AI_MODEL_PATH` · `AI_N_GPU_LAYERS(-1)` · `AI_N_CTX(4096)` · `AI_TEMPERATURE(0.2)` · `AI_MAX_NEW_TOKENS(700)`
4. Runtime: llama-cpp-python 0.3.x in-process; this machine runs the CPU build (nvcc absent); GPU offload needs the CUDA toolkit install below; `AI_N_GPU_LAYERS` is a safe no-op on CPU
   ```bash
   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
   ```
5. Python 3.14 has no prebuilt wheel yet — source-build fallback expected

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
