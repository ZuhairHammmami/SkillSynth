"""Local GGUF inference engine — guarded lazy singleton (SS-AI).

Called only by services/llm_pipeline.py; loads the model file from
config.app_settings.AI_MODEL_PATH once, serializes completions through
a semaphore, and degrades to LLMUnavailable instead of crashing the
app when the artifact is absent (spec Failure Handling).
"""
import logging
import threading

from backend.config import app_settings as settings
from backend.services import settings_service

logger = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """Raised when inference is requested but the engine cannot serve."""


_lock = threading.Lock()
_semaphore = threading.Semaphore(1)
_llm = None
_load_failed = False
_TOTAL_LAYERS = 28
_HEADROOM_MB = 1400


def reset_for_tests() -> None:
    """Clear singleton/latch state between tests.

    Called by the autouse fixture in tests/test_llm_engine.py.
    """
    global _llm, _load_failed
    with _lock:
        _llm = None
        _load_failed = False


def reset_load_failure() -> None:
    """Clear the failed-load latch so the engine may retry a cold start.

    Dependencies: locks _lock and clears the module-level _load_failed flag.
    Implementation: used by warmup() and available() self-healing so a
    transient VRAM-occupied load failure auto-recovers once resources free
    (no process restart required). Safe to call when no failure is latched.
    """
    global _load_failed
    with _lock:
        _load_failed = False


def available() -> bool:
    """True iff enabled, artifact exists and the engine can serve.

    Dependencies: reads settings_service.is_ai_enabled(), calls
    _model_path_exists() and _get_llm(). Implementation: self-heals a prior
    _load_failed latch when AI is still enabled and the artifact exists —
    resets the latch and retries the load once so a transient VRAM-occupied
    failure recovers automatically (no restart). Used by routers/ai.py and
    pipeline callers.
    """
    if _load_failed and settings_service.is_ai_enabled() \
            and _model_path_exists():
        reset_load_failure()
        try:
            _get_llm()
        except LLMUnavailable:
            return False
    return bool(settings_service.is_ai_enabled()) and not _load_failed and \
        _model_path_exists()


def health() -> dict:
    """Diagnostics payload for status endpoints/logs.

    Dependencies: reads settings.AI_ENABLED/AI_MODEL_PATH and calls
    available()/_model_path_exists(). Implementation: returns a snapshot of
    enablement, artifact existence, load state and the live availability gate.
    Consumed by admin system-health surfacing and tests.
    """
    return {"enabled": bool(settings_service.is_ai_enabled()),
            "path": settings.AI_MODEL_PATH,
            "artifact_exists": _model_path_exists(),
            "loaded": _llm is not None,
            "available": available()}


def warmup() -> bool:
    """Force-load the model now; True when serving afterwards.

    Dependencies: calls reset_load_failure() then _get_llm(), logs via logger.
    Implementation: clears any prior failed-load latch and triggers the lazy
    singleton load eagerly; swallows LLMUnavailable and returns False instead
    of crashing. Called at startup (non-fatal) and by tests.
    """
    reset_load_failure()
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


def _fit_layers(free_mb: int, model_bytes: int, requested: int) -> int:
    """Cap GPU offload to what fits available VRAM (default all-gpu OOMs).

    Dependencies: none (pure). Called by _get_llm to derive n_gpu_layers.
    Implementation: an explicit requested>=0 always wins; otherwise (the -1
    "all layers" default) estimate the layer count that fits by multiplying
    the fixed layer count by the VRAM budget fraction (free minus a fixed
    context/activations headroom, over model file size there too), clamped to
    [0, total]. Returns 0 (CPU-only) when VRAM/scaling is non-positive so a
    small GPU degrades instead of OOMing.
    """
    if requested >= 0:
        return requested
    model_mb = model_bytes / (1024 * 1024)
    if free_mb <= 0 or model_mb <= 0:
        return 0
    usable = max(0, free_mb - _HEADROOM_MB)
    fraction = min(1.0, usable / model_mb)
    return max(0, min(_TOTAL_LAYERS, round(_TOTAL_LAYERS * fraction)))


def _free_vram_mb() -> int:
    """Best-effort free VRAM in MB, or 0 when no usable GPU is found.

    Dependencies: lazily imports shutil/subprocess. Called by _get_llm to
    size GPU offload. Implementation: parses `nvidia-smi`'s first GPU free
    memory value; returns 0 when the binary or any value is absent so the
    caller falls back to CPU-only (no GPU = nothing to offload). Non-fatal.
    """
    import shutil
    import subprocess
    if shutil.which("nvidia-smi") is None:
        return 0
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3).stdout.strip()
        first = out.splitlines()[0].strip() if out else ""
        return int(first) if first.isdigit() else 0
    except Exception:  # noqa: BLE001 — best-effort probe is non-fatal
        return 0


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
        if not settings_service.is_ai_enabled():
            raise LLMUnavailable("AI_ENABLED is false")
        if not _model_path_exists():
            _load_failed = True
            raise LLMUnavailable(f"model file missing: {settings.AI_MODEL_PATH}")
        try:
            import os
            from llama_cpp import Llama
            _llm = Llama(
                model_path=settings.AI_MODEL_PATH,
                n_ctx=settings.AI_N_CTX,
                n_gpu_layers=_fit_layers(
                    _free_vram_mb(),
                    os.path.getsize(settings.AI_MODEL_PATH),
                    settings.AI_N_GPU_LAYERS),
                verbose=False,
            )
            return _llm
        except Exception as exc:  # noqa: BLE001 — degrade, never crash app
            _load_failed = True
            logger.error("SS-AI engine load failed: %s", exc)
            raise LLMUnavailable(str(exc)) from exc
