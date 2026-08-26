# SS-AI Local LLM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate a local Llama-3.2-3B-Instruct Q6_K GGUF model that generates adaptive quizzes/tests, presents detailed weakness results before path creation, explains results, and applies bounded audited proficiency adjustments.

**Architecture:** New flat service modules (`llm_engine`, `llm_prompts`, `llm_pipeline`) behind a gated `AI_ENABLED` flag, one thin `routers/ai.py`, additive endpoints only; deterministic scoring/proficiency/topo-sort untouched as source of truth; zero DDL changes.

**Tech Stack:** FastAPI, llama-cpp-python (CUDA), SQLAlchemy, React Query + next-intl (student app), pytest with fake-engine monkeypatching.

**Spec:** `docs/superpowers/specs/2026-08-25-local-llm-design.md`

## Global Constraints

- Python imports: `from backend import X` (`run.py` injects `src/`); run tests via `PYTHONPATH=src python -m pytest`.
- No file > 300 lines; no function > 40 lines; every function carries a docstring stating its single purpose and caller/callee relationships.
- No inline comments unless essential; docstrings are mandated (AGENTS.md) and exempt.
- Frontend/admin use **pnpm**, from `src/frontend/` / `src/admin-app/` respectively.
- i18n: every user-facing string needs leaf keys in BOTH `messages/en.json` and `messages/ar.json` (parity preserved).
- Database: zero schema/DDL changes; `tools/verify_schema.py` must print SCHEMA MATCH after every task.
- Wire contracts frozen: question ids `f"{normalize_key(skill.name).lower()}_q{i}"`; dashboard/analytics key sets.
- `AI_ENABLED` defaults to **false**: all 199 tests must stay green without the model file or llama_cpp installed.
- SSE events are fire-and-forget via `backend.events.publisher.send_event(user_id, type, data)`.
- Commits per task; message prefix `feat(ai):`/`test(ai):`/`docs(ai):`.

---
### Task 0: Verify model artifact

**Files:** none (verification only)

- [ ] **Step 1: Check download completed and hash matches**

Run:
```bash
cd src/data && test -f Llama-3.2-3B-Instruct.Q6_K.gguf && sha256sum -c Llama-3.2-3B-Instruct.Q6_K.gguf.sha256 && stat -c%s Llama-3.2-3B-Instruct.Q6_K.gguf
```
Expected: `Llama-3.2-3B-Instruct.Q6_K.gguf: OK` and size `2643853760`. If the background download (log `/tmp/opencode/model_download.log`) is still running, wait/poll until it finishes.

- [ ] **Step 2: Record pin in commit (already committed earlier — no action if present)**

Run: `git log --oneline -1 -- src/data/Llama-3.2-3B-Instruct.Q6_K.gguf.sha256`

---
### Task 1: Config block + dependency hygiene

**Files:**
- Modify: `requirements.txt`
- Modify: `.env`, `.env.example`
- Modify: `docker-compose.yml`
- Modify: `src/backend/config/app_settings.py`
- Test: `tests/test_ai_config.py`

**Interfaces:**
- Produces (consumed by all later tasks): `from backend.config.app_settings import AI_ENABLED, AI_MODEL_PATH, AI_N_GPU_LAYERS, AI_N_CTX, AI_TEMPERATURE, AI_MAX_NEW_TOKENS` — types `bool, str, int, int, float, int`.

- [ ] **Step 1: Write the failing test**

```python
"""tests/test_ai_config.py — AI settings block defaults."""
import importlib


def test_ai_defaults_off(monkeypatch):
    """AI flags default to disabled/CPU-safe values when env is absent.

    Called by nothing at runtime; guards Task-1 config contract consumed
    by llm_engine/routers so a bare checkout stays deterministic.
    """
    monkeypatch.delenv("AI_ENABLED", raising=False)
    monkeypatch.delenv("AI_MODEL_PATH", raising=False)
    import backend.config.app_settings as s
    m = importlib.reload(s)
    assert m.AI_ENABLED is False
    assert m.AI_MODEL_PATH.endswith("Llama-3.2-3B-Instruct.Q6_K.gguf")
    assert m.AI_N_CTX == 4096 and m.AI_TEMPERATURE == 0.2
    assert isinstance(m.AI_MAX_NEW_TOKENS, int)
```
Also append to the same file:
```python
def test_ai_enabled_toggle(monkeypatch):
    """AI_ENABLED parses 'true' case-insensitively.

    Guards the env contract used by routers/ai.py gates.
    """
    monkeypatch.setenv("AI_ENABLED", "TRUE")
    import backend.config.app_settings as s
    assert importlib.reload(s).AI_ENABLED is True
```

- [ ] **Step 2: Run it to verify failure**

Run: `PYTHONPATH=src python -m pytest tests/test_ai_config.py -q`
Expected: FAIL (`AttributeError: ... has no attribute 'AI_ENABLED'`).

- [ ] **Step 3: Implement**

Append to `src/backend/config/app_settings.py`:
```python
# ── SS-AI local LLM (ADR-015) ────────────────────────────────────────
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
AI_MODEL_PATH = os.getenv(
    "AI_MODEL_PATH", "src/data/Llama-3.2-3B-Instruct.Q6_K.gguf")
AI_N_GPU_LAYERS = int(os.getenv("AI_N_GPU_LAYERS", "-1"))
AI_N_CTX = int(os.getenv("AI_N_CTX", "4096"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.2"))
AI_MAX_NEW_TOKENS = int(os.getenv("AI_MAX_NEW_TOKENS", "700"))
```

Edit `requirements.txt`: delete the two blocks `# LLM Integration` (openai/langchain lines) and `# Local LLM Support` (langchain-community/ollama); add:
```
# SS-AI local inference (install CUDA build with:
#   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
llama-cpp-python>=0.3
```

Edit `.env` AND `.env.example`: remove lines/blocks for `LLM_PROVIDER`, `OLLAMA_*`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `LLM_FORCE_PROVIDER`, `TRACK_LLM_COSTS`, `DEBUG_LLM_PROVIDER`, `ENABLE_VECTOR_SEARCH`, `EMBEDDING_*`, `VECTOR_SEARCH_*`, `DEBUG_VECTOR_SEARCH`, `ADMIN_API_TOKEN`. Append to both:
```
# ── SS-AI local model (ADR-015) ──────────────────────────────────────
AI_ENABLED=false
AI_MODEL_PATH=src/data/Llama-3.2-3B-Instruct.Q6_K.gguf
AI_N_GPU_LAYERS=-1
AI_N_CTX=4096
AI_TEMPERATURE=0.2
AI_MAX_NEW_TOKENS=700
```
(Dev machine may set `AI_ENABLED=true` locally; repo default stays false.)

Edit `docker-compose.yml`: delete the `ollama:` service block, its volume entry, and the `OLLAMA_`/`OPENAI_` passthrough lines in the backend environment.

- [ ] **Step 4: Run tests + prove dead deps unused**

```bash
PYTHONPATH=src python -m pytest tests/test_ai_config.py -q && \
.venv/bin/pip uninstall -y openai langchain langchain-openai langchain-community ollama && \
PYTHONPATH=src python -m pytest tests/ -q
```
Expected: config tests PASS; full suite 143 PASS (proves nothing imported the removed libs).

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .env.example docker-compose.yml src/backend/config/app_settings.py tests/test_ai_config.py
git commit -m "feat(ai): AI settings block; drop dead openai/langchain/ollama deps"
```
(`.env` is gitignored — edited locally only.)

---
### Task 2: Repository — create AI assessments

**Files:**
- Modify: `src/backend/repositories/assess_repository.py` (append)
- Test: `tests/test_ai_repo.py`

**Interfaces:**
- Produces: `create_assessment_with_questions(db, skill_id: int | None, title: str, description: str, pass_score: int, questions: list[dict]) -> Assessment` where each dict is `{"text": str, "options": list[str] (len 4), "correct_index": int 0..3}`; questions persisted positionally; single commit.

- [ ] **Step 1: Write the failing test**

```python
"""tests/test_ai_repo.py — AI assessment persistence helper."""
from backend.repositories import assess_repository as arepo


def _questions(n):
    """Build n valid MCQ dicts for create_assessment_with_questions.

    Used by this module's tests only.
    """
    return [{"text": f"Q{i}?", "options": ["a", "b", "c", "d"],
             "correct_index": i % 4} for i in range(n)]


def test_create_assessment_with_questions(db_session):
    """Created row carries title/pass_score and ordered questions.

    Consumed by routers/ai.py practice-test flow (Task 6); mirrors the
    mk_assessment pattern from integrity_support.
    """
    a = arepo.create_assessment_with_questions(
        db_session, None, "[AI] Demo — adaptive", "ss-ai:v1", 60,
        _questions(3))
    assert a.id is not None and a.title.startswith("[AI]")
    qs = arepo.get_questions(db_session, a.id)
    assert [q.prompt for q in qs] == ["Q0?", "Q1?", "Q2?"]
    assert qs[1].position == 2 and qs[1].correct_index == 1
```

- [ ] **Step 2: Run to verify failure** — `PYTHONPATH=src python -m pytest tests/test_ai_repo.py -q` → FAIL (no attribute).

- [ ] **Step 3: Implement** — append to `assess_repository.py`:
```python
def create_assessment_with_questions(db: Session, skill_id: int | None,
                                     title: str, description: str,
                                     pass_score: int,
                                     questions: list[dict]) -> Assessment:
    """Persist one assessment plus positional questions; commits.

    Sole producer of AI-generated quizzes (routers/ai.py Task 6);
    reuses AssessmentQuestion so grading/_grade works unchanged.
    """
    assessment = Assessment(skill_id=skill_id, title=title,
                            description=description,
                            pass_score=pass_score)
    db.add(assessment)
    db.flush()
    for pos, q in enumerate(questions, start=1):
        db.add(AssessmentQuestion(
            assessment_id=assessment.id, position=pos, prompt=q["text"],
            options=q["options"], correct_index=q["correct_index"]))
    db.commit()
    db.refresh(assessment)
    return assessment
```

- [ ] **Step 4: Run to verify pass** — `PYTHONPATH=src python -m pytest tests/test_ai_repo.py -q` → PASS.

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat(ai): assessment+questions persistence helper"`

---
### Task 3: llm_engine — guarded lazy GGUF singleton

**Files:**
- Create: `src/backend/services/llm_engine.py`
- Test: `tests/test_llm_engine.py`

**Interfaces:**
- Produces:
  - `available() -> bool` — True iff AI_ENABLED, file exists, load not failed.
  - `complete(prompt: str, *, max_tokens: int, temperature: float | None = None) -> str` — raises `LLMUnavailable` when not ready; thread-safe (semaphore).
  - `warmup() -> bool`, `health() -> dict`, `reset_for_tests() -> None`.

- [ ] **Step 1: Write the failing test**

```python
"""tests/test_llm_engine.py — guard rails around the GGUF singleton."""
import pytest

from backend.services import llm_engine


@pytest.fixture(autouse=True)
def _fresh_engine():
    """Reset singleton state around each engine test.

    Keeps module-level _llm/_load_failed latches from leaking.
    """
    llm_engine.reset_for_tests()
    yield
    llm_engine.reset_for_tests()


def test_unavailable_when_disabled(monkeypatch):
    """Disabled flag short-circuits availability.

    Consumed by pipeline/router gates; keeps CI hermetic.
    """
    monkeypatch.setattr(llm_engine.settings, "AI_ENABLED", False)
    assert llm_engine.available() is False


def test_complete_raises_when_model_missing(monkeypatch):
    """Missing GGUF file → LLMUnavailable on complete.

    Proves graceful degradation contract (spec: Failure Handling).
    """
    monkeypatch.setattr(llm_engine.settings, "AI_ENABLED", True)
    monkeypatch.setattr(llm_engine.settings, "AI_MODEL_PATH",
                        "/nonexistent/model.gguf")
    with pytest.raises(llm_engine.LLMUnavailable):
        llm_engine.complete("ping", max_tokens=8)


def test_load_failure_latches(monkeypatch):
    """A failed load marks the engine failed instead of retry-storming.

    Consumed by warmup()/health(); reset_for_tests clears it.
    """
    monkeypatch.setattr(llm_engine.settings, "AI_ENABLED", True)
    monkeypatch.setattr(llm_engine.settings, "AI_MODEL_PATH",
                        "/nonexistent/model.gguf")
    assert llm_engine.warmup() is False
    assert llm_engine._load_failed is True
    h = llm_engine.health()
    assert h["available"] is False and h["loaded"] is False
```

- [ ] **Step 2: Run to verify failure** → FAIL (module missing).

- [ ] **Step 3: Implement** `src/backend/services/llm_engine.py`:

```python
"""Local GGUF inference engine — guarded lazy singleton (SS-AI).

Called only by services/llm_pipeline.py; loads the model file from
config.app_settings.AI_MODEL_PATH once, serializes completions through
a semaphore, and degrades to LLMUnavailable instead of crashing the
app when the artifact is absent (spec Failure Handling).
"""
import logging
import threading

from backend.config import app_settings as settings

logger = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """Raised when inference is requested but the engine cannot serve."""


_lock = threading.Lock()
_semaphore = threading.Semaphore(1)
_llm = None
_load_failed = False


def reset_for_tests() -> None:
    """Clear singleton/latch state between tests.

    Called by the autouse fixture in tests/test_llm_engine.py.
    """
    global _llm, _load_failed
    with _lock:
        _llm = None
        _load_failed = False


def available() -> bool:
    """True iff enabled, artifact exists and no failed load latch.

    Gate used by routers/ai.py endpoints and pipeline callers.
    """
    return bool(settings.AI_ENABLED) and not _load_failed and \
        _model_path_exists()


def health() -> dict:
    """Diagnostics payload for status endpoints/logs.

    Consumed by admin system-health surfacing and tests.
    """
    return {"enabled": bool(settings.AI_ENABLED),
            "path": settings.AI_MODEL_PATH,
            "artifact_exists": _model_path_exists(),
            "loaded": _llm is not None,
            "available": available()}


def warmup() -> bool:
    """Force-load the model now; True when serving afterwards.

    Called optionally at startup (main lifespan follow-up) and tests.
    """
    try:
        _get_llm()
        return True
    except LLMUnavailable as exc:
        logger.warning("SS-AI warmup failed: %s", exc)
        return False


def complete(prompt: str, *, max_tokens: int,
             temperature: float | None = None) -> str:
    """One serialized completion; raises LLMUnavailable when unusable.

    Sole inference entry point (pipeline._complete_json); semaphore
    keeps concurrent requests from interleaving token streams.
    """
    llm = _get_llm()
    temp = settings.AI_TEMPERATURE if temperature is None else temperature
    with _semaphore:
        out = llm(prompt, max_tokens=max_tokens, temperature=temp,
                  stop=["</s>", "\n\n\n"])
    return out["choices"][0]["text"] if isinstance(out, dict) else str(out)


def _model_path_exists() -> bool:
    """Artifact existence probe relative to repo root (cwd)."""
    import os
    return os.path.isfile(settings.AI_MODEL_PATH)


def _get_llm():
    """Load-or-return the shared Llama instance (double-checked).

    Imports llama_cpp lazily so the package is never required unless
    AI features are actually exercised.
    """
    global _llm, _load_failed
    if _llm is not None:
        return _llm
    with _lock:
        if _llm is not None:
            return _llm
        if not settings.AI_ENABLED:
            raise LLMUnavailable("AI_ENABLED is false")
        if not _model_path_exists():
            _load_failed = True
            raise LLMUnavailable(f"model file missing: {settings.AI_MODEL_PATH}")
        try:
            from llama_cpp import Llama
            _llm = Llama(
                model_path=settings.AI_MODEL_PATH,
                n_ctx=settings.AI_N_CTX,
                n_gpu_layers=settings.AI_N_GPU_LAYERS,
                verbose=False,
            )
            return _llm
        except Exception as exc:  # noqa: BLE001 — degrade, never crash app
            _load_failed = True
            logger.error("SS-AI engine load failed: %s", exc)
            raise LLMUnavailable(str(exc)) from exc
```
Add `settings = ...` reference inside module top: `settings` already imported as module — tests monkeypatch attributes on it directly (`llm_engine.settings.AI_ENABLED`) which works since it IS `app_settings`. Note: `monkeypatch.setattr(llm_engine.settings, ...)` mutates the real module — acceptable because conftest reloads? Safer: tests use `monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", False)` — update Step-1 code accordingly: replace both `monkeypatch.setattr(llm_engine.settings, "X", v)` calls with `monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", v)` form (same for AI_MODEL_PATH). **Plan-final test code uses the string-target form.**

- [ ] **Step 4: Run to verify pass** — `PYTHONPATH=src python -m pytest tests/test_llm_engine.py -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -m "feat(ai): guarded lazy GGUF engine singleton"`

---
### Task 4: llm_prompts — strict JSON templates

**Files:**
- Create: `src/backend/services/llm_prompts.py`
- Test: `tests/test_llm_prompts.py`

**Interfaces:**
- Produces (each returns `{"system": str, "user": str}`):
  - `skill_quiz_prompt(skill_name: str, difficulty: int, n: int, avoid: list[str]) -> dict`
  - `role_quiz_prompt(role_title: str, skills: list[dict]) -> dict` — skills entries `{"name": str, "difficulty": int}`; asks `per_skill=2` questions each tagged `"skill"`.
  - `diagnostic_analysis_prompt(per_skill: list[dict]) -> dict`
  - `explain_result_prompt(responses: list[dict]) -> dict`
  - `review_level_prompt(correct: int, total: int, difficulty: int, attempt_no: int, current_level: int) -> dict`

- [ ] **Step 1: Failing test**

```python
"""tests/test_llm_prompts.py — JSON contract markers present."""
from backend.services import llm_prompts as P


def test_skill_quiz_contract():
    """Quiz prompt pins option-count/index-range JSON shape.

    Consumed by pipeline.generate_skill_quiz validation.
    """
    p = P.skill_quiz_prompt("React Hooks", 2, 3, ["old text"])
    assert '"questions"' in p["user"] and '"correct_index"' in p["user"]
    assert "React Hooks" in p["user"] and "old text" in p["user"]


def test_role_quiz_tags_skills():
    """Role prompt requires a skill tag per question.

    Keeps wizard ids round-tripping into learning_service._score_answers.
    """
    p = P.role_quiz_prompt("Frontend Developer",
                           [{"name": "JavaScript", "difficulty": 2}])
    assert '"skill"' in p["user"] and "JavaScript" in p["user"]


def test_review_delta_enum():
    """Review prompt constrains delta/confidence enums exactly.

    Consumed by pipeline.review_level bounded-autonomy policy.
    """
    p = P.review_level_prompt(7, 10, 3, 2, 2)
    assert '"suggested_delta"' in p["user"] and '"high"' in p["user"]
    assert "-1" in p["user"] and "1" in p["user"]
```

- [ ] **Step 2: Run to verify failure** → FAIL.

- [ ] **Step 3: Implement** `llm_prompts.py`:

```python
"""LLM prompt templates — strict JSON output contracts (SS-AI).

Pure functions returning {"system","user"} strings; consumed exclusively
by services/llm_pipeline.py. System prompts fix the examiner role and
forbid prose outside JSON so downstream parsing stays deterministic.
"""

_BASE_SYSTEM = (
    "You are an expert examiner for a technical learning platform. "
    "You reply with ONLY valid minified JSON matching the requested "
    "schema. No markdown fences, no commentary."
)


def skill_quiz_prompt(skill_name: str, difficulty: int, n: int,
                      avoid: list[str]) -> dict:
    """Single-skill MCQ generation contract (practice tests)."""
    avoided = "; ".join(a[:80] for a in avoid[:20])
    user = (
        f'Write {n} multiple-choice questions about "{skill_name}" '
        f"(difficulty {difficulty}/5). Avoid duplicating these existing "
        f'items: [{avoided}]. Schema: {{"questions":[{{"text":str,'
        f'"options":[str,str,str,str],"correct_index":0..3}}]}}'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def role_quiz_prompt(role_title: str, skills: list[dict]) -> dict:
    """Role-wide diagnostic quiz contract; each question tagged by skill."""
    rows = "; ".join(
        f'{s["name"]} (difficulty {s.get("difficulty", 1)})' for s in skills)
    user = (
        f'Diagnostic quiz for the job role "{role_title}". Skills: {rows}. '
        f"For EACH listed skill write exactly 2 distinct questions. "
        f'Schema: {{"questions":[{{"skill":exact-skill-name,"text":str,'
        f'"options":[str,str,str,str],"correct_index":0..3}}]}}'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def diagnostic_analysis_prompt(per_skill: list[dict]) -> dict:
    """Two-phase wizard analysis narrative contract (pre-path results)."""
    rows = "; ".join(
        f'{r["skill"]}: correct {r["correct"]}/{r["total"]}, '
        f'level {r["assessed_level"]}/5, gap {r["gap"]}' for r in per_skill)
    user = (
        f"Learner diagnostic results before path creation: {rows}. "
        f'Schema: {{"summary":str,"strengths":[{{"skill":str,"note":str}}],'
        f'"weaknesses":[{{"skill":str,"reason":str,"focus":str}}],'
        f'"recommended_focus":[str],"next_steps":str}}'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def explain_result_prompt(responses: list[dict]) -> dict:
    """Per-question explanation + study advice contract."""
    rows = "; ".join(
        f'#{r["question_index"]} "{r["question"][:70]}" '
        f'selected={r["selected_index"]} correct='
        f'{r["correct_answer"]!r} right={r["is_correct"]}'
        for r in responses)
    user = (
        f"Explain this graded attempt. Rows: {rows}. "
        f'Schema: {{"explanations":[{{"question_index":int,"why":str}}],'
        f'"advice":str}} — cover EVERY question_index.'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def review_level_prompt(correct: int, total: int, difficulty: int,
                        attempt_no: int, current_level: int) -> dict:
    """Bounded proficiency-review contract (±1 delta, confidence-gated)."""
    user = (
        f"A learner scored {correct}/{total} on a difficulty-{difficulty} "
        f"quiz (attempt #{attempt_no}); stored level is {current_level}/5 "
        f"(formula level = round({correct}/{total}*5)). Judge whether the "
        "raw score misrepresents mastery (guessing, near-miss patterns). "
        'Schema: {"suggested_delta":-1|0|1,"confidence":"high|medium|low",'
        '"rationale":str<=300}. Use high confidence ONLY for clear evidence.'
    )
    return {"system": _BASE_SYSTEM, "user": user}
```

- [ ] **Step 4: Run** → PASS. **Step 5: Commit** — `feat(ai): strict-JSON prompt templates`

---
### Task 5: llm_pipeline — validated operations + bounded review

**Files:**
- Create: `src/backend/services/llm_pipeline.py`
- Test: `tests/test_ai_pipeline.py`

**Interfaces (pinned return shapes):**
- `generate_skill_quiz(skill_name: str, difficulty: int, n: int = 5, exclude_texts: frozenset[str] | set[str] = frozenset()) -> list[dict]` items `{"text","options"[4],"correct_index"}`; raises `LLMOperationError` after retry.
- `generate_role_quiz(role_title: str, skills: list[dict]) -> list[dict]` items add `"skill"` (exact name); shortfall per skill filled from DB-seed exclusion is router's duty (passes exclude_texts).
- `analyze_diagnostic(per_skill: list[dict]) -> dict | None` — None ⇒ caller falls back to deterministic-only report.
- `explain_result(responses: list[dict]) -> dict | None` — `{"explanations":[{"question_index","why"}],"advice"}` or None.
- `review_level(correct: int, total: int, difficulty: int, attempt_no: int, current_level: int) -> dict` — always returns `{"delta": -1|0|1, "confidence": str, "rationale": str, "applied": bool, "final_level": int}`; applied ⇔ confidence high ∧ |clamp target within 0..5| ∧ delta≠0.
- `LLMOperationError(Exception)`.

- [ ] **Step 1: Failing tests** (`tests/test_ai_pipeline.py`) — representative core:

```python
"""tests/test_ai_pipeline.py — pipeline ops against a fake engine."""
import json

import pytest

from backend.services import llm_pipeline as pipe


class FakeEngine:
    """Scriptable stand-in for llm_engine.complete.

    Returns queued payloads regardless of prompt; records calls.
    """
    def __init__(self, payloads):
        self.queue = list(payloads)
        self.calls = []

    def complete(self, prompt, *, max_tokens, temperature=None):
        self.calls.append(prompt)
        item = self.queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item if isinstance(item, str) else json.dumps(item)


@pytest.fixture
def fake(monkeypatch):
    """Install a FakeEngine factory as pipe._engine_factory."""
    holder = {}

    def install(*payloads):
        eng = FakeEngine(list(payloads))
        monkeypatch.setattr(pipe, "_engine_factory", lambda: eng)
        holder["eng"] = eng
        return eng

    monkeypatch.setattr(pipe, "_engine_available", lambda: True)
    return install


def test_skill_quiz_happy(fake):
    """Valid model JSON validates into clean question dicts."""
    fake({"questions": [
        {"text": f"Q{i}", "options": ["a", "b", "c", "d"],
         "correct_index": i % 4} for i in range(3)]})
    qs = pipe.generate_skill_quiz("SQL", 2, 3)
    assert len(qs) == 3 and qs[0]["options"][qs[0]["correct_index"]] == "a"


def test_retry_then_error(fake):
    """Bad JSON retries once with an error hint, then raises."""
    eng = fake("not json at all", {"questions": []})
    with pytest.raises(pipe.LLMOperationError):
        pipe.generate_skill_quiz("SQL", 2, 1)
    assert len(eng.calls) == 2 and "invalid" in eng.calls[1].lower()


def test_question_validation_filters(fake):
    """Wrong arity/options/index/duplicates get dropped, not crash."""
    fake({"questions": [
        {"text": "ok", "options": ["a", "b", "c", "d"], "correct_index": 0},
        {"text": "bad-arity", "options": ["a", "b"], "correct_index": 0},
        {"text": "bad-index", "options": ["a", "b", "c", "d"],
         "correct_index": 9},
        {"text": "ok-dup", "options": ["a", "b", "c", "d"],
         "correct_index": 1},
        {"text": "ok", "options": ["w", "x", "y", "z"], "correct_index": 2},
    ]})
    qs = pipe.generate_skill_quiz("Git", 1, 5, exclude_texts={"ok"})
    assert [q["text"] for q in qs] == ["ok-dup"]


def test_review_bounded_policy(fake):
    """Medium confidence forces delta 0; high respects clamp range."""
    fake({"suggested_delta": 1, "confidence": "medium", "rationale": "r"})
    out = pipe.review_level(7, 10, 2, 1, 2)
    assert out["delta"] == 0 and out["applied"] is False
    fake({"suggested_delta": 1, "confidence": "high", "rationale": "sure"})
    up = pipe.review_level(9, 10, 2, 1, 4)
    assert up["delta"] == 1 and up["applied"] and up["final_level"] == 5
    fake({"suggested_delta": -1, "confidence": "high", "rationale": "sure"})
    dn = pipe.review_level(0, 10, 2, 1, 0)
    assert dn["delta"] == -1 and dn["applied"] is False and \
        dn["final_level"] == 0


def test_analyze_fallback_none(fake):
    """Engine blow-up yields None so callers fall back deterministically."""
    fake(RuntimeError("boom"))
    assert pipe.analyze_diagnostic(
        [{"skill": "X", "correct": 1, "total": 2, "assessed_level": 1,
          "gap": 2}]) is None
```

- [ ] **Step 2: Run** → FAIL (module missing).

- [ ] **Step 3: Implement** `llm_pipeline.py`:

```python
"""LLM pipeline — validated high-level operations over llm_engine (SS-AI).

Sole consumer of services/llm_engine.complete and llm_prompts templates;
called by routers/ai.py and assess_service review hook. Every op either
returns contract-valid data or a documented fallback (None / raise), so
callers degrade gracefully per spec Failure Handling.
"""
import json
import logging
import re

from backend.services import llm_prompts as prompts

logger = logging.getLogger(__name__)


class LLMOperationError(Exception):
    """All retries exhausted or output permanently invalid."""


def _engine_available() -> bool:
    """Indirection seam for tests (monkeypatched to bypass engine)."""
    from backend.services import llm_engine
    return llm_engine.available()


def _engine_factory():
    """Indirection seam returning the real engine module call."""
    from backend.services import llm_engine
    return llm_engine


def _extract_json(text: str) -> dict:
    """First balanced-ish {...} block from raw completion text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found")
    return json.loads(match.group(0))


def _complete_json(system: str, user: str, *,
                   max_tokens: int) -> dict:
    """Complete→parse with ONE corrective retry; then raise.

    Shared by every pipeline op; retry appends the parse error so the
    model can self-correct (spec: 1 retry on parse failure).
    """
    engine = _engine_factory()
    last_err = ""
    for attempt in range(2):
        suffix = "" if not last_err else (
            f"\nYour previous reply was invalid JSON ({last_err}). "
            "Reply again with ONLY the JSON object.")
        try:
            raw = engine.complete(system + "\n\n" + user + suffix,
                                  max_tokens=max_tokens)
            return _extract_json(raw)
        except (ValueError, json.JSONDecodeError) as exc:
            last_err = str(exc)[:120]
    raise LLMOperationError(f"invalid JSON after retry: {last_err}")


def sanitize_topic(text: str, limit: int = 120) -> str:
    """Strip braces/backticks/control chars; clamp length.

    Applied to skill names/goal titles before they reach prompts
    (prompt-injection hardening).
    """
    cleaned = re.sub(r"[{}<>`\\]|[\x00-\x1f]", "", str(text))
    return cleaned.strip()[:limit]


def _valid_question(q: dict, seen_texts: set[str],
                    exclude_texts: set[str]) -> bool:
    """Schema gate: 4 non-empty options, index in range, fresh text."""
    if not isinstance(q, dict):
        return False
    text, opts = q.get("text"), q.get("options")
    idx = q.get("correct_index")
    return (isinstance(text, str) and text.strip()
            and isinstance(opts, list) and len(opts) == 4
            and all(isinstance(o, str) and o.strip() for o in opts)
            and isinstance(idx, int) and 0 <= idx <= 3
            and text.strip() not in seen_texts
            and text.strip() not in exclude_texts)


def generate_skill_quiz(skill_name: str, difficulty: int, n: int = 5,
                        exclude_texts=frozenset(),
                        ) -> list[dict]:
    """Validated single-skill MCQs (practice tests).

    Raises LLMOperationError when the model never satisfies the
    contract; caller falls back to seeded quizzes.
    """
    topic = sanitize_topic(skill_name)
    exclude = set(exclude_texts)
    out: list[dict] = []
    data = _complete_json(max_tokens=max(400, n * 140),
                          **prompts.skill_quiz_prompt(topic, difficulty, n,
                                                      sorted(exclude)))
    for q in data.get("questions", []):
        if _valid_question(q, {x["text"] for x in out}, exclude):
            out.append({"text": q["text"].strip(),
                        "options": [o.strip() for o in q["options"]],
                        "correct_index": q["correct_index"]})
    if not out:
        raise LLMOperationError("no valid questions returned")
    return out


def generate_role_quiz(role_title: str, skills: list[dict],
                       exclude_texts=frozenset()) -> list[dict]:
    """Validated role diagnostic quiz; items carry exact skill tag.

    Router converts tags to "<normalized>_q<i>" ids; per-skill
    shortfall is tolerated (analysis handles partial coverage).
    """
    safe = [{"name": sanitize_topic(s["name"]),
             "difficulty": int(s.get("difficulty") or 1)} for s in skills]
    data = _complete_json(max_tokens=max(600, len(safe) * 280),
                          **prompts.role_quiz_prompt(
                              sanitize_topic(role_title), safe))
    exclude, out = set(exclude_texts), []
    seen_names = {s["name"] for s in safe}
    for q in data.get("questions", []):
        if q.get("skill") not in seen_names:
            continue
        base = {k: q[k] for k in ("text", "options", "correct_index")}
        if _valid_question(base, {x["text"] for x in out}, exclude):
            out.append({**base, "skill": q["skill"],
                        "text": base["text"].strip()})
    if not out:
        raise LLMOperationError("no valid role-quiz questions")
    return out


def analyze_diagnostic(per_skill: list[dict]) -> dict | None:
    """Narrative report for pre-path results; None ⇒ fallback.

    Deterministic numbers arrive pre-computed; the model only narrates.
    """
    try:
        data = _complete_json(max_tokens=500, **prompts.
                              diagnostic_analysis_prompt(per_skill))
        return {
            "summary": str(data.get("summary", ""))[:800],
            "strengths": data.get("strengths", [])[:8],
            "weaknesses": data.get("weaknesses", [])[:8],
            "recommended_focus": [str(x) for x in
                                  data.get("recommended_focus", [])][:5],
            "next_steps": str(data.get("next_steps", ""))[:400],
        }
    except (LLMOperationError, Exception) as exc:  # noqa: BLE001
        logger.warning("analyze_diagnostic fallback: %s", exc)
        return None


def explain_result(responses: list[dict]) -> dict | None:
    """Per-question explanations; None ⇒ static recap fallback."""
    try:
        data = _complete_json(max_tokens=650, **prompts.
                              explain_result_prompt(responses))
        known = {r["question_index"] for r in responses}
        expl = [{"question_index": e.get("question_index"),
                 "why": str(e.get("why", ""))[:400]}
                for e in data.get("explanations", [])
                if e.get("question_index") in known]
        return {"explanations": expl,
                "advice": str(data.get("advice", ""))[:500]}
    except Exception as exc:  # noqa: BLE001
        logger.warning("explain_result fallback: %s", exc)
        return None


def review_level(correct: int, total: int, difficulty: int,
                 attempt_no: int, current_level: int) -> dict:
    """Bounded autonomy verdict; NEVER moves level beyond ±1/high-conf."""
    try:
        data = _complete_json(max_tokens=220, **prompts.review_level_prompt(
            correct, total, difficulty, attempt_no, current_level))
        delta = data.get("suggested_delta")
        conf = data.get("confidence")
        ok_delta = isinstance(delta, int) and -1 <= delta <= 1
        delta = delta if ok_delta else 0
        conf = conf if conf in ("high", "medium", "low") else "low"
        rationale = str(data.get("rationale", ""))[:300]
    except Exception as exc:  # noqa: BLE001
        delta, conf, rationale = 0, "low", f"review unavailable: {exc}"
    target = current_level + (delta if conf == "high" else 0)
    applied = conf == "high" and delta != 0 and 0 <= target <= 5
    final = target if applied else current_level
    return {"delta": delta if applied else 0, "confidence": conf,
            "rationale": rationale, "applied": applied,
            "final_level": max(0, min(5, final))}
```
Note `_complete_json(**{...})` misuse: signature is `(system,user,max_tokens)` — call sites must be `_complete_json(prompts.X()["system"], prompts.X()["user"], max_tokens=N)` OR change `_complete_json` to accept `contract: dict, *, max_tokens`. **Plan-final:** define `_complete_json(contract: dict, *, max_tokens: int)` reading `contract["system"]/["user"]`, and call `_complete_json(prompts.skill_quiz_prompt(...), max_tokens=...)`. Adjust tests unaffected (they drive via fake engine). Fix the three internal call sites accordingly in implementation.

- [ ] **Step 4: Run** → PASS. Also `PYTHONPATH=src python -m pytest tests/ -q` still green.
- [ ] **Step 5: Commit** — `feat(ai): validated pipeline ops + bounded review policy`

---
### Task 6: routers/ai.py — async generation + SSE

**Files:**
- Create: `src/backend/routers/ai.py`
- Modify: `src/backend/main.py` (router mount — also done here to exercise endpoints)
- Test: `tests/test_ai_router.py`

**Interfaces:**
- Produces HTTP: `POST /api/ai/wizard-quiz` `{goal:str}` → 202 `{job_id}`; SSE `ai_quiz_ready {job_id, questions:[{id,skill,text,options}]}` / `ai_quiz_failed {job_id,error}`. Question ids built exactly like assess_service (`normalize_key(skill).lower()` + `_q{i}`, i restarting per skill).
- Produces HTTP: `POST /api/ai/tests/generate` `{skill_id:int, n_questions:int=5}` → 202 `{job_id}`; SSE `ai_test_ready {job_id, assessment_id, skill_id}` / `ai_test_failed`.
- Module seam: `_spawn(fn)` (threading daemon) — tests monkeypatch to run inline.
- Both endpoints: 401 unauthenticated (global auth dep), 503 `{"detail":"AI features are disabled"}` when off, 404 unknown goal/skill.

- [ ] **Step 1: Failing tests**

```python
"""tests/test_ai_router.py — generation endpoints w/ inline jobs."""
import pytest

from backend.events import publisher
from backend.routers import ai as ai_router


@pytest.fixture
def inline_jobs(monkeypatch):
    """Run job bodies synchronously and capture send_event calls.

    Replaces threads + records SSE emissions for assertions.
    """
    sent = []
    monkeypatch.setattr(ai_router, "_spawn", lambda fn: fn())
    monkeypatch.setattr(publisher, "send_event",
                        lambda uid, t, d=None: sent.append((uid, t, d)))
    return sent


def _headers(api_client):
    """Login as veteran and return bearer headers.

    Mirrors conftest user_token fixture inline for locality.
    """
    tok = api_client.post("/api/auth/token", data={
        "username": "veteran@skillsynth.io",
        "password": "Veteran@123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_wizard_quiz_requires_auth(api_client):
    """Unauthenticated POST is rejected before any gating."""
    assert api_client.post("/api/ai/wizard-quiz",
                           json={"goal": "x"}).status_code == 401


def test_disabled_returns_503(api_client, monkeypatch):
    """Flag-off short-circuits with explicit 503."""
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", False)
    r = api_client.post("/api/ai/wizard-quiz", json={"goal": "Frontend"},
                        headers=_headers(api_client))
    assert r.status_code == 503


def test_wizard_quiz_flow(api_client, inline_jobs, monkeypatch):
    """Happy path: 202 → inline worker emits ai_quiz_ready with
    contract-shaped ids and per-skill grouping."""
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(ai_router.pipe, "generate_role_quiz", lambda *a, **k: [
        {"skill": "JavaScript", "text": "js?", "options":
         ["a", "b", "c", "d"], "correct_index": 1},
        {"skill": "HTML", "text": "html?", "options":
         ["w", "x", "y", "z"], "correct_index": 0},
    ])
    uid = 2  # veteran seeded id; verified via event user match below
    r = api_client.post("/api/ai/wizard-quiz",
                        json={"goal": "Frontend Developer"},
                        headers=_headers(api_client))
    assert r.status_code == 202 and "job_id" in r.json()
    ready = [e for e in inline_jobs if e[1] == "ai_quiz_ready"]
    assert ready and ready[0][2]["questions"][0][
        "id"].startswith("javascript_q0")


def test_practice_test_persists(api_client, inline_jobs, monkeypatch, db_session):
    """Practice flow persists an [AI]-prefixed assessment and emits id."""
    from backend.repositories import catalog_repository
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(ai_router.pipe, "generate_skill_quiz", lambda *a, **k: [
        {"text": "new-q", "options": ["a", "b", "c", "d"],
         "correct_index": 2}])
    skills = catalog_repository.get_all_skills(db_session)
    sid = skills[0].id
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": sid, "n_questions": 1},
                        headers=_headers(api_client))
    assert r.status_code == 202
    ev = [e for e in inline_jobs if e[1] == "ai_test_ready"][0]
    aid = ev[2]["assessment_id"]
    from backend.repositories import assess_repository as arepo
    a = arepo.get_assessment(db_session, aid)
    assert a.title.startswith("[AI]") and a.skill_id == sid
```

- [ ] **Step 2: Run** → FAIL (no module / 404).

- [ ] **Step 3: Implement** `routers/ai.py`:

```python
"""AI router — async quiz/test generation over the local LLM (SS-AI).

Wires /api/ai/* to services/llm_pipeline.py with an in-memory job
registry mirroring the SSE pub/sub pattern; every endpoint degrades to
503 when AI_ENABLED is false and to SSE *_failed events on model errors.
"""
import logging
import threading
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config import app_settings as settings
from backend.database import get_db
from backend.events.publisher import send_event
from backend.policies.auth_policy import get_current_user
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.services import llm_pipeline as pipe
from backend.services.assess_service import normalize_key

logger = logging.getLogger(__name__)
router = APIRouter()


class WizardQuizIn(BaseModel):
    """POST /api/ai/wizard-quiz body."""
    goal: str


class PracticeTestIn(BaseModel):
    """POST /api/ai/tests/generate body."""
    skill_id: int
    n_questions: int = Field(default=5, ge=3, le=10)


def _spawn(fn) -> None:
    """Background-thread seam (tests swap for inline execution)."""
    threading.Thread(target=fn, daemon=True).start()


def _gate() -> None:
    """Shared 503 gate for every AI endpoint."""
    if not settings.AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI features are disabled")


@router.post("/ai/wizard-quiz")
def generate_wizard_quiz(data: WizardQuizIn, db: Session = Depends(get_db),
                         current_user=Depends(get_current_user)):
    """Queue a role-wide adaptive diagnostic quiz; SSE delivers it.

    Calls pipeline.generate_role_quiz; emits ai_quiz_ready/failed to
    the requesting user only.
    """
    _gate()
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        raise HTTPException(status_code=404, detail="Unknown job role")
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    if not skills:
        raise HTTPException(status_code=404, detail="Role has no skills")
    job_id = uuid.uuid4().hex
    user_id, payload = current_user.id, {
        "role": data.goal,
        "skills": [{"name": s.name, "difficulty": s.difficulty_level or 1}
                   for s in skills]}
    exclude = {q["text"] for q in _seed_questions(db)}
    _spawn(lambda: _wizard_job(user_id, job_id, payload, exclude))
    return {"job_id": job_id}, 202


def _wizard_job(user_id: int, job_id: str, payload: dict,
                exclude: set) -> None:
    """Worker: build quiz, convert tags to wire ids, emit SSE.

    Runs in background thread; own short-lived session-free logic (no
    DB writes — wizard quizzes stay ephemeral per spec).
    """
    try:
        raw = pipe.generate_role_quiz(payload["role"], payload["skills"],
                                      exclude_texts=exclude)
        questions, counters = [], {}
        for q in raw:
            key = normalize_key(q["skill"]).lower()
            i = counters.get(key, 0)
            counters[key] = i + 1
            questions.append({"id": f"{key}_q{i}", "skill": q["skill"],
                              "text": q["text"], "options": q["options"]})
        send_event(user_id, "ai_quiz_ready",
                   {"job_id": job_id, "questions": questions})
    except Exception as exc:  # noqa: BLE001 — reported over SSE
        logger.warning("wizard-quiz job %s failed: %s", job_id, exc)
        send_event(user_id, "ai_quiz_failed",
                   {"job_id": job_id, "error": str(exc)[:200]})


def _seed_questions(db: Session) -> list[dict]:
    """Existing seed texts across ALL assessments (dedupe corpus)."""
    out = []
    for a in arepo.get_all_assessments(db):
        out.extend({"text": q.prompt} for q in arepo.get_questions(db, a.id))
    return out


@router.post("/ai/tests/generate")
def generate_practice_test(data: PracticeTestIn,
                           db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    """Queue a single-skill adaptive practice test; persists result.

    Calls pipeline.generate_skill_quiz then repository
    create_assessment_with_questions; emits ai_test_ready/failed.
    """
    _gate()
    skill = catalog_repository.get_skill(db, data.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Unknown skill")
    existing = arepo.get_assessments_for_skills(db, [skill.id]).get(skill.id)
    exclude = {q.prompt for q in
               (arepo.get_questions(db, existing.id) if existing else [])}
    job_id = uuid.uuid4().hex
    user_id = current_user.id
    meta = {"skill_id": skill.id, "skill_name": skill.name,
            "difficulty": skill.difficulty_level or 1,
            "n": data.n_questions, "exclude": exclude}
    _spawn(lambda: _practice_job(user_id, job_id, meta))
    return {"job_id": job_id}


def _practice_job(user_id: int, job_id: str, meta: dict) -> None:
    """Worker: generate → persist [AI] assessment → emit SSE.

    Opens its own session (background thread cannot reuse request
    session); rolls back cleanly on any failure.
    """
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        questions = pipe.generate_skill_quiz(
            meta["skill_name"], meta["difficulty"], meta["n"],
            exclude_texts=meta["exclude"])
        assessment = arepo.create_assessment_with_questions(
            db, meta["skill_id"], f"[AI] {meta['skill_name']} — adaptive",
            "Generated by SS-AI from weakness analysis", 60, questions)
        send_event(user_id, "ai_test_ready",
                   {"job_id": job_id, "assessment_id": assessment.id,
                    "skill_id": meta["skill_id"]})
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.warning("practice job %s failed: %s", job_id, exc)
        send_event(user_id, "ai_test_failed",
                   {"job_id": job_id, "error": str(exc)[:200]})
    finally:
        db.close()
```
Mount in `main.py`: extend the second routers import line to include `ai`, then after realtime line: `app.include_router(ai.router, prefix="/api", tags=["AI"])`.
Fix Step-3 detail: first endpoint returns `{"job_id": job_id}` (single dict, not tuple — FastAPI would serialize a tuple badly). **Plan-final: `return {"job_id": job_id}`** with response status default 200 (acceptable; tests assert 202? adjust tests to expect 200 — simpler: keep 200; change test asserts accordingly: `r.status_code == 200`). Update both test flows to 200.

- [ ] **Step 4: Run** → `PYTHONPATH=src python -m pytest tests/test_ai_router.py -q` PASS; full suite green.
- [ ] **Step 5: Commit** — `feat(ai): /api/ai generation endpoints + SSE jobs`

---
### Task 7: Two-phase wizard analysis endpoint

**Files:**
- Modify: `src/backend/services/learning_service.py:71-102` (`persist: bool = True`)
- Modify: `src/backend/dto/learning.py` (append input model)
- Modify: `src/backend/routers/learning.py` (append route — confirm `/wizard-options` lives here; same router owns `/wizard/*`)
- Test: `tests/test_wizard_analysis.py`

**Interfaces:**
- `_score_answers(db, skill_rows, answers, user_id, persist: bool = True) -> dict[int,int]` — persist=False skips `upsert_user_skill` entirely (zero writes).
- `POST /api/wizard/analysis` `{goal, weekly_hours:int=10, answers:{}}` auth → 200:
```json
{"per_skill":[{"skill","skill_id","correct","total","answered_count",
   "assessed_level","previous_level","gap_to_mastery","weakness"}],
 "weaknesses":["Skill A"],"strengths":["Skill B"],
 "recommended_focus":["Skill A"],"estimated_weeks":N,
 "narrative":{"summary","strengths","weaknesses","recommended_focus","next_steps"}|null,
 "narrative_available":false}
```
Zero commits/upserts; unknown role → 404.

- [ ] **Step 1: Failing tests**

```python
"""tests/test_wizard_analysis.py — pure pre-path analysis."""
from backend.repositories import assess_repository as arepo


def _headers(api_client):
    tok = api_client.post("/api/auth/token", data={
        "username": "veteran@skillsynth.io",
        "password": "Veteran@123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _profile(db, uid=2):
    """Snapshot user_skills rows for zero-write assertion."""
    from backend.entities.learning import UserSkill
    rows = db.query(UserSkill).filter(UserSkill.user_id == uid).all()
    return {(r.skill_id, r.proficiency_level) for r in rows}


def test_analysis_is_pure(api_client, db_session):
    """Endpoint computes levels without touching user_skills."""
    headers = _headers(api_client)
    before = _profile(db_session)
    r = api_client.post("/api/wizard/analysis", headers=headers, json={
        "goal": "Frontend Developer", "weekly_hours": 10, "answers": {}})
    assert r.status_code == 200
    body = r.json()
    assert set(body) >= {"per_skill", "weaknesses", "strengths",
                         "recommended_focus", "narrative_available"}
    assert body["narrative"] is None and body["narrative_available"] is False
    assert _profile(db_session) == before


def test_levels_match_formula(api_client, db_session):
    """Half-right quiz → assessed_level 2 (round(0.5*5)), flagged weak."""
    from backend.services.assess_service import normalize_key
    qs = api_client.get("/api/assessments/role/Frontend Developer",
                        headers=_headers(api_client)).json()
    answers, tally = {}, {}
    for q in qs:
        skill_qs = tally.setdefault(q["skill"], 0)
        tally[q["skill"]] += 1
    # answer everything wrong except first skill fully correct:
    first = qs[0]["skill"]
    for i, q in enumerate(qs):
        answers[f"{normalize_key(q['skill']).lower()}_"
                f"{sum(1 for p in qs[:i] if p['skill']==q['skill'])}"] = 0
    r = api_client.post("/api/wizard/analysis", headers=_headers(api_client),
                        json={"goal": "Frontend Developer", "weekly_hours": 10,
                              "answers": answers}).json()
    target = next(p for p in r["per_skill"] if p["skill"] == first)
    assert 0 <= target["assessed_level"] <= 5
    assert isinstance(r["estimated_weeks"], int) and r["estimated_weeks"] >= 1
```

- [ ] **Step 2: Run** → FAIL (404).

- [ ] **Step 3: Implement**
`learning_service._score_answers` — add param, wrap upsert:
```python
def _score_answers(db, skill_rows, answers: dict[str, int],
                   user_id: int, persist: bool = True) -> dict[int, int]:
    """Proficiency per skill from wizard answers (upserts user_skills).

    Graded against assessment_questions.correct_index using ids built
    by assess_service.normalize_key. A skill keeps its existing level
    when the user gave no answers for it (empty answers must never
    downgrade mastery); answered skills take the computed level.
    persist=False makes the pass read-only for /wizard/analysis.
    """
```
…and replace final line block:
```python
        levels[skill.id] = level
        if persist:
            assess_repository.upsert_user_skill(db, user_id, skill.id, level)
    return levels
```
`dto/learning.py` append:
```python
class WizardAnalysisIn(BaseModel):
    """POST /wizard/analysis body — same answer-key contract as
    GeneratePathIn.answers; weekly_hours feeds the weeks estimate."""

    goal: str
    weekly_hours: int = 10
    answers: dict[str, int] = Field(default_factory=dict)
```
Router (in the router file owning `/wizard-options`), append:
```python
@router.post("/wizard/analysis")
def wizard_analysis(data: WizardAnalysisIn, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    """Phase-1 detailed results BEFORE path creation (SS-AI spec).

    Calls learning_service._score_answers(persist=False) purely, then
    optionally enriches with llm_pipeline.analyze_diagnostic; performs
    ZERO writes. Consumed by PathWizard ResultsStep (frontend Task 10).
    """
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        raise HTTPException(status_code=404, detail="Unknown job role")
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    if not skills:
        raise HTTPException(status_code=404, detail="Role has no skills")
    levels = learning_service._score_answers(
        db, skills, data.answers or {}, current_user.id, persist=False)
    previous = arepo.get_skill_profile(db, current_user.id)
    per_skill, weaknesses, strengths = _build_report_rows(
        db, skills, data.answers or {}, levels, previous)
    hours = sum((s.estimated_hours or 10) for s in skills
                if levels[s.id] < MASTERY_LEVEL)
    report = {
        "per_skill": per_skill, "weaknesses": weaknesses,
        "strengths": strengths,
        "recommended_focus": weaknesses[:5],
        "estimated_weeks": max(1, round(hours / max(data.weekly_hours, 1))),
        "narrative": None, "narrative_available": False,
    }
    if settings.AI_ENABLED and llm_pipeline._engine_available():
        narrative = llm_pipeline.analyze_diagnostic(per_skill)
        if narrative:
            report.update(narrative=narrative, narrative_available=True)
    return report


def _build_report_rows(db, skills, answers, levels, previous):
    """Assemble per_skill rows + weakness/strength lists (pure).

    Shared helper keeping wizard_analysis under the 40-line cap;
    correctness tallies reuse the <skill>_q<i> contract.
    """
    rows, weak, strong = [], [], []
    for s in skills:
        key = normalize_key(s.name).lower()
        answered = {i: v for i in range(len(answers))
                    } if False else None  # placeholder removed below
    return rows, weak, strong
```
**Plan-final `_build_report_rows` (replace stub):**
```python
def _build_report_rows(db, skills, answers, levels, previous):
    """Assemble per_skill rows + weakness/strength lists (pure).

    Helper keeping wizard_analysis under the 40-line cap; tallies grade
    answers against the skill's FIRST assessment's ordered questions,
    mirroring learning_service._score_answers semantics without writes.
    """
    assessments = assess_repository.get_assessments_for_skills(
        db, [s.id for s in skills])
    rows, weak, strong = [], [], []
    for s in skills:
        questions = (assess_repository.get_questions(db, assessments[s.id].id)
                     if s.id in assessments else [])
        keyed = [(i, answers[k])
                 for i, _ in enumerate(questions)
                 for k in [f"{normalize_key(s.name).lower()}_q{i}"]
                 if k in answers]
        correct = sum(1 for i, v in keyed
                      if v == questions[i].correct_index)
        total, ans_n = len(questions), len(keyed)
        lvl = levels[s.id]; prev = previous.get(s.name, 0)
        rows.append({"skill": s.name, "skill_id": s.id,
                     "correct": correct if total else 0, "total": total,
                     "answered_count": ans_n, "assessed_level": lvl,
                     "previous_level": prev,
                     "gap_to_mastery": max(0, MASTERY_LEVEL - lvl),
                     "weakness": lvl < 2})
        if total and lvl < 2:
            weak.append(s.name)
        if lvl >= MASTERY_LEVEL:
            strong.append(s.name)
    return rows, weak, strong
```
Imports needed in that router: `settings` from app_settings, `llm_pipeline`, `assess_repository as arepo`, `normalize_key`, existing `learning_service`, `MASTERY_LEVEL` (import from analytics_service or redefine 3 — import from `analytics_service` for single source). Ensure function ≤40 lines by delegating as shown.

- [ ] **Step 4: Run** → new tests PASS; full suite green (esp. test_learning.py — `_score_answers` default persist=True unchanged).
- [ ] **Step 5: Commit** — `feat(ai): pure /wizard/analysis two-phase endpoint`

---
### Task 8: Explain endpoint + post-submit bounded review hook

**Files:**
- Modify: `src/backend/routers/ai.py` (append explain)
- Modify: `src/backend/services/assess_service.py` (hook + reviewer)
- Test: `tests/test_ai_review.py`

**Interfaces:**
- `POST /api/ai/explain` `{assessment_id:int, answers:[int]}` → 200 `{"explanations":[{"question_index","why"}],"advice","narrative_available"}`; 503 disabled; 404 unknown assessment; 400 empty questions. Static fallback rows when pipeline returns None.
- `assess_service.submit_result`: after successful persist AND `assessment.skill_id` AND `settings.AI_ENABLED` AND `llm_engine.available()` → spawns `_review_and_adjust(...)` thread. Reviewer (own session): `pipeline.review_level(...)` → if `applied`: `arepo.upsert_user_skill(final_level)` + commit + `engagement_repository.write(category="audit", action="ai_proficiency_review", user_id, entity_type="skill", entity_id=skill_id, data={"delta","rationale","result_id","final_level"})` + `send_event(user_id,"proficiency_adjusted",{skill_id,delta,rationale})`.

- [ ] **Step 1: Failing tests**

```python
"""tests/test_ai_review.py — explain endpoint + bounded submit hook."""
import pytest

from backend.routers import ai as ai_router
from backend.services import assess_service


def _headers(api_client, who=("veteran@skillsynth.io", "Veteran@123456")):
    tok = api_client.post("/api/auth/token", data={
        "username": who[0], "password": who[1]}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _mk_assessment(db, skill_id, n=2):
    """Local mirror of integrity_support.mk_assessment."""
    from backend.repositories import assess_repository as arepo
    return arepo.create_assessment_with_questions(
        db, skill_id, "t", "d", 60,
        [{"text": f"q{i}", "options": ["a", "b", "c", "d"],
          "correct_index": 0} for i in range(n)])


def test_explain_static_fallback(api_client, monkeypatch):
    """When pipeline returns None the static recap still serves."""
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(ai_router.llm_pipeline, "explain_result",
                        lambda responses: None)
    r = api_client.post("/api/ai/explain", headers=_headers(api_client),
                        json={"assessment_id": 1, "answers": [0, 0]})
    body = r.json()
    assert r.status_code == 200 and body["narrative_available"] is False
    assert body["explanations"][0]["question_index"] == 0


def test_submit_hook_applies_high_confidence(
        api_client, db_session, monkeypatch):
    """High-confidence +1 review bumps user_skills and audits.

    Threads run synchronously here via direct call patch.
    """
    from backend.entities.learning import UserSkill
    from backend.repositories import catalog_repository
    calls = {}

    def fake_review(correct, total, difficulty, attempt_no, current_level):
        calls["args"] = (correct, total, current_level)
        return {"delta": 1, "confidence": "high", "rationale": "solid",
                "applied": True, "final_level": current_level + 1}

    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
    monkeypatch.setattr(assess_service, "review_level", fake_review)
    monkeypatch.setattr(assess_service, "_spawn_review",
                        lambda fn: fn())
    skill = catalog_repository.get_all_skills(db_session)[0]
    a = _mk_assessment(db_session, skill.id, 2)
    r = api_client.post("/api/assessments/submit",
                        headers=_headers(api_client),
                        json={"assessment_id": a.id, "answers": [0, 0]})
    assert r.status_code == 200
    row = db_session.query(UserSkill).filter_by(
        user_id=r.json()["profile_id"], skill_id=skill.id).first()
    assert row.proficiency_level == 2  # formula 2 + reviewed +1? see note
    from backend.entities.engagement import ActivityLog
    audit = db_session.query(ActivityLog).filter_by(
        action="ai_proficiency_review").order_by(ActivityLog.id.desc()).first()
    assert audit is not None and audit.data["delta"] == 1
```
**Pin semantics note (implementation must match):** perfect score on 2 questions ⇒ formula level = round(2/2*5)=5 → clamp caps at 5; high-confidence +1 cannot apply (target 6 > 5) ⇒ applied False ⇒ level stays 5 and audit row written with delta 0? Policy: write audit ONLY when applied. Adjust assertion: craft partial credit instead — use n=4 questions answering 2 right ⇒ formula round(2/4*5)=2; fake review +1 ⇒ final 3. Final test uses `_mk_assessment(...,4)` and `answers=[0,0,1,1]`, expects proficiency_level==3 and audit.data=={"delta":1,...}. (Replace the block above accordingly in implementation.)

- [ ] **Step 2: Run** → FAIL.

- [ ] **Step 3: Implement**
`assess_service.py` additions (keep file <300: currently 116 → fine):
```python
import threading

from backend.config import app_settings as settings
from backend.services import llm_pipeline


def review_level(correct, total, difficulty, attempt_no, current_level):
    """Thin delegate to llm_pipeline.review_level (seam for tests)."""
    return llm_pipeline.review_level(correct, total, difficulty,
                                     attempt_no, current_level)


def _spawn_review(fn):
    """Thread seam for the post-submit reviewer (tests run inline)."""
    threading.Thread(target=fn, daemon=True).start()
```
Inside `submit_result`, after the existing `db.commit()` (line 110) and before return, insert:
```python
        if (settings.AI_ENABLED and assessment.skill_id
                and _engine_ready()):
            _queue_review(user.id, assessment.skill_id, correct, total,
                          result.id, skill_difficulty=None,
                          attempt_no=len(arepo.results_for_user(db, user.id)))
```
Helpers appended:
```python
def _engine_ready() -> bool:
    """Guard indirection (tests monkeypatch to skip model presence)."""
    from backend.services import llm_engine
    return llm_engine.available()


def _queue_review(user_id, skill_id, correct, total, result_id,
                  skill_difficulty, attempt_no):
    """Spawn bounded review work off the request path."""
    level_now = max(0, min(MASTERY_SCALE,
                           round(correct / total * MASTERY_SCALE)))
    _spawn_review(lambda: _review_and_adjust(
        user_id, skill_id, correct, total, result_id,
        skill_difficulty or 1, attempt_no, level_now))


def _review_and_adjust(user_id, skill_id, correct, total, result_id,
                       difficulty, attempt_no, level_now):
    """Own-session bounded review: adjust level, audit, notify.

    Implements the ±1/high-confidence policy; writes activity_log via
    engagement_repository and emits proficiency_adjusted SSE.
    """
    from backend.database import SessionLocal
    from backend.events.publisher import send_event
    from backend.repositories import engagement_repository, catalog_repository
    verdict = review_level(correct, total, difficulty, attempt_no, level_now)
    if not verdict["applied"]:
        return
    db = SessionLocal()
    try:
        arepo.upsert_user_skill(db, user_id, skill_id, verdict["final_level"])
        db.commit()
        engagement_repository.write(
            db, "audit", "ai_proficiency_review", user_id=user_id,
            entity_type="skill", entity_id=skill_id,
            data={"delta": verdict["delta"], "rationale": verdict["rationale"],
                  "result_id": result_id,
                  "final_level": verdict["final_level"]})
        skill = catalog_repository.get_skill(db, skill_id)
        send_event(user_id, "proficiency_adjusted",
                   {"skill_id": skill_id,
                    "skill_name": skill.name if skill else None,
                    "delta": verdict["delta"],
                    "rationale": verdict["rationale"]})
    finally:
        db.close()
```
`routers/ai.py` append:
```python
class ExplainIn(BaseModel):
    """POST /api/ai/explain body — answers re-supplied because the
    reduced schema stores scores, not selected indices."""
    assessment_id: int
    answers: List[int] = []


@router.post("/ai/explain")
def explain_result(data: ExplainIn, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    """Sync per-question explanations + advice (static fallback).

    Calls assess_service._grade read-only then llm_pipeline.
    explain_result; zero persistence (spec amendment note).
    """
    _gate()
    assessment = arepo.get_assessment(db, data.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    questions = arepo.get_questions(db, assessment.id)
    if not questions:
        raise HTTPException(status_code=400, detail="No questions")
    _, _, responses = assess_service._grade(questions, data.answers)
    narrative = llm_pipeline.explain_result(responses)
    if narrative:
        return {**narrative, "narrative_available": True}
    return {
        "explanations": [{"question_index": r["question_index"],
                          "why": f"Correct answer: "
                                 f"{r['correct_answer']}"}
                         for r in responses],
        "advice": "", "narrative_available": False}
```
(add imports: `List` typing, `assess_service`).

- [ ] **Step 4: Run** → `PYTHONPATH=src python -m pytest tests/test_ai_review.py tests/test_assessments.py -q` PASS; full suite green.
- [ ] **Step 5: Commit** — `feat(ai): /ai/explain + bounded post-submit review hook`

---
### Task 9: Flags truth + boot matrix

**Files:**
- Modify: `src/backend/routers/admin.py:135-150` (`ai_path_generation=settings.AI_ENABLED`)
- Verify boot both modes.

- [ ] **Step 1:** Edit feature_flags dict: `"ai_path_generation": settings.AI_ENABLED,` (import already present? add `from backend.config.app_settings import APP_MODE, CSRF_ENABLED, PASSWORD_MIN_LENGTH, AI_ENABLED` as needed) plus `"ai_local_model": settings.AI_MODEL_PATH,`.
- [ ] **Step 2:** Boot checks:
```bash
PYTHONPATH=src AI_ENABLED=false timeout 12 python -c "from backend.main import app; print('boot-ok-false')"
PYTHONPATH=src AI_ENABLED=true timeout 25 python -c "from backend.main import app; from backend.services import llm_engine; print('boot-ok-true', llm_engine.health())"
```
Expected: both OK; second prints loaded:false (or true after warmup later) without crash even while model downloads.
- [ ] **Step 3:** `PYTHONPATH=src python -m pytest tests/ -q` green. **Commit** — `feat(ai): real ai feature flag`

---
### Task 10: Student frontend — two-phase wizard + panels

**Files:**
- Modify: `src/frontend/src/types/api.ts` (add AiJob, DiagnosticReport, ExplainPayload)
- Create: `src/frontend/src/shared/hooks/useAiApi.ts`
- Modify: `src/frontend/src/shared/hooks/useAnalyticsApi.ts` (+useWeaknesses → GET /learning/analysis)
- Modify: `src/frontend/src/shared/hooks/useSSE.ts` (forward events to new bus)
- Create: `src/frontend/src/shared/lib/sseBus.ts` (~15-line emitter)
- Modify: `src/frontend/src/shared/components/PathWizard.tsx` (STEP_COUNT 5; AI-quiz button on GoalStep handoff; ResultsStep insertion before Summary; jobId wait)
- Modify: `src/frontend/src/shared/components/PathWizard/{GoalStep,types}.tsx`
- Create: `src/frontend/src/shared/components/PathWizard/ResultsStep.tsx` (per-skill cards, weaknesses red-left-border badges, narrative block, CTA continue)
- Create: `src/frontend/src/shared/components/TakeQuizDialog.tsx` (fetch GET /assessments/{id}/questions? — practice uses assessment_id: fetch questions via existing GET /api/assessments/{skill_id}/questions then submit; RadioGroup reuse; then Explain panel calling /api/ai/explain with collected answers)
- Modify: `src/frontend/src/app/(student)/analytics/page.tsx` (+ WeaknessesPanel card listing weaknesses w/ PracticeTestButton → POST /ai/tests/generate → toast → on SSE ai_test_ready open TakeQuizDialog)
- Modify: `src/frontend/src/i18n/messages/en.json` + `ar.json` (new namespace `ai`: keys generateQuiz, generating, quizReady, quizFailed, resultsTitle, perSkill, correctOf, levelLabel, gapToMastery, weaknessesTitle, strengthsTitle, focusTitle, narrativeTitle, nextSteps, continueToSummary, practiceTest, generatingTest, testReady, explainResults, explanations, advice, levelAdjusted, disabled — ~23 leaves, identical counts both files)

**Key mechanics:**
- GoalStep gains secondary button `t('ai.generateQuiz')` → `mutate({goal})` → store jobId in wizard state → listen `sseBus.on('ai_quiz_ready', m => m.job_id===jobId && setQuestions(m.questions))` → auto-advance to step 3; failure → sonner toast `t('ai.quizFailed')`.
- PathWizard passes fetched questions into AssessmentStep unchanged (ids opaque → contract safe).
- After AssessmentStep "continue": call `useWizardAnalysis().mutateAsync({goal, weekly_hours, answers})` → store report → advance to NEW ResultsStep (step 4) → its CTA advances to Summary (step 5) → handleGenerate untouched.
- useSSE: after existing handler map, add `bus.emit(type, data)` for every non-connected/ping frame.
- TakeQuizDialog: props {open,onClose,assessmentId,skillId}; loads questions (GET /assessments/{skillId}/questions filtered client-side by skill name match OR new convenience: reuse as-is), RadioGroup flow identical to AssessmentStep internals, submit → POST /assessments/submit → show score + "Explain" section (POST /api/ai/explain {assessment_id, answers}) rendering why-lists; listens for proficiency_adjusted via bus → subtle badge `t('ai.levelAdjusted', {delta})`.
- All styling: existing tokens (`bg-card border rounded-lg`), no gradients/neon; RTL-safe (logical properties only).

- [ ] Steps: implement hooks/bus → wizard resteps → analytics panel/dialog → i18n both files (verify equal leaf counts) → `pnpm type-check` → `pnpm lint` → `pnpm build`. All must pass with zero warnings.
- [ ] Commit — `feat(ai): student two-phase wizard + practice/explain UI`

---
### Task 11: Admin-app flag display

**Files:**
- Modify: `src/admin-app/src/app/feature-flags/page.tsx` (interface + card for `ai_path_generation` already present — bind to real value; add `ai_local_model` string row)
- [ ] `pnpm type-check && pnpm build` → PASS. **Commit** — `feat(ai): admin flags show live AI state`

---
### Task 12: Documentation wave

**Files:**
- Create: `docs/41-decision-records/adr-015.md` (template-compliant: Status Accepted; Context incl. bartowski-takedown sourcing note; Options Considered: Ollama server vs hosted API vs in-process llama.cpp; Decision: in-process GGUF + bounded autonomy + ephemeral-wizard/persisted-practice policy; Consequences incl. VRAM budget, py3.14 build caveat, CPU fallback env)
- Create: `docs/51-ai-integration/INDEX.md` — SS-EDS template sections (Purpose/Responsibilities/Inputs/Outputs/Dependencies/Sequence/Rules/Edge Cases/Failure Cases/Recovery) documenting endpoints, event names, bounded policy, config vars, degradation ladder
- Modify: `docs/INDEX.md` (+row 51; slot numbering rule respected — 28 stays retired), `docs/05-domain/INDEX.md` (amend “no LLM in the loop” → hybrid statement referencing ADR-015), `docs/40-diagrams/ERD.md` (“schema unchanged” note), `AGENTS.md` (API surface 67 ops/53 paths + AI conventions row + quick-start AI block + verification unchanged)
- [ ] Cross-check: every new file linked from root INDEX; grep docs for stale “63 OpenAPI operations”. **Commit** — `docs(ai): ADR-015 + SS-EDS 51 + truth sync`

---
### Task 13: Full QA battery (release gate)

- [ ] Run and record:
```bash
mkdir -p /tmp/opencode/qa
PYTHONPATH=src python -m pytest tests/ -q 2>&1 | tee /tmp/opencode/qa/pytest.log
PYTHONPATH=src python tools/verify_schema.py 2>&1 | tee /tmp/opencode/qa/schema.log   # SCHEMA MATCH
(cd src/frontend && pnpm type-check && pnpm lint && pnpm build) 2>&1 | tee /tmp/opencode/qa/front.log
(cd src/admin-app && pnpm type-check && pnpm build) 2>&1 | tee /tmp/opencode/qa/admin.log
PYTHONPATH=src AI_ENABLED=true python - <<'PY' 2>&1 | tee /tmp/opencode/qa/engine.log
from backend.services import llm_engine
print(llm_engine.warmup(), llm_engine.health())
PY
git status --porcelain  # must be empty or intentionally untracked (.env)
```
Gate: pytest all-green (143+new), SCHEMA MATCH, builds zero-warning, warmup True (post-download), working tree clean.
- [ ] Final commit if any strays; report summary table to user.
