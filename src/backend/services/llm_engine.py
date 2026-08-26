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

    Dependencies: reads settings.AI_ENABLED and calls _model_path_exists().
    Implementation: short-circuits on the _load_failed latch so a prior
    missing/misloaded artifact is not retried on every gate check. Used by
    routers/ai.py endpoints and pipeline callers.
    """
    return bool(settings.AI_ENABLED) and not _load_failed and \
        _model_path_exists()


def health() -> dict:
    """Diagnostics payload for status endpoints/logs.

    Dependencies: reads settings.AI_ENABLED/AI_MODEL_PATH and calls
    available()/_model_path_exists(). Implementation: returns a snapshot of
    enablement, artifact existence, load state and the live availability gate.
    Consumed by admin system-health surfacing and tests.
    """
    return {"enabled": bool(settings.AI_ENABLED),
            "path": settings.AI_MODEL_PATH,
            "artifact_exists": _model_path_exists(),
            "loaded": _llm is not None,
            "available": available()}


def warmup() -> bool:
    """Force-load the model now; True when serving afterwards.

    Dependencies: calls _get_llm() and logs via logger. Implementation:
    triggers the lazy singleton load eagerly; swallows LLMUnavailable and
    returns False instead of crashing. Called optionally at startup and tests.
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

    Dependencies: calls _get_llm(), reads settings for temperature/repeat/
    top_p defaults, and logs via logger. Implementation: the sole inference
    entry point (pipeline._complete_json); a semaphore keeps concurrent
    requests from interleaving token streams. Applies anti-degeneration
    sampling unless the caller overrides temperature. Returns the text field
    when the backend yields a dict, else the raw string.
    """
    llm = _get_llm()
    temp = settings.AI_TEMPERATURE if temperature is None else temperature
    with _semaphore:
        out = llm(prompt, max_tokens=max_tokens, temperature=temp,
                  repeat_penalty=settings.AI_REPEAT_PENALTY,
                  top_p=settings.AI_TOP_P,
                  stop=["</s>", "\n\n\n"])
    return out["choices"][0]["text"] if isinstance(out, dict) else str(out)


def _model_path_exists() -> bool:
    """Artifact existence probe relative to repo root (cwd).

    Dependencies: lazily imports os and reads settings.AI_MODEL_PATH.
    Implementation: a plain os.path.isfile check; intentionally lazy so the
    os import cost is paid only when availability is actually queried.
    """
    import os
    return os.path.isfile(settings.AI_MODEL_PATH)


def _get_llm():
    """Load-or-return the shared Llama instance (double-checked).

    Dependencies: reads settings (AI_ENABLED, AI_MODEL_PATH, AI_N_CTX,
    AI_N_GPU_LAYERS), lazily imports llama_cpp.Llama, and logs. Implementation:
    double-checked locking returns a cached instance; on first load sets the
    _load_failed latch for a missing model or any import/inference error so
    the app degrades instead of crashing. llama_cpp is imported lazily so the
    package is never required unless AI is exercised.
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
