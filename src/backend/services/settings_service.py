"""Runtime settings persistence — file-backed JSON store (no DB table).

Provides a runtime-toggle for AI features without breaking the strict
15-table database invariant. Settings persist to src/data/settings.json,
seeded from the AI_ENABLED env var on first access. Consumed by
routers/ai.py, routers/admin.py, services/llm_engine.py,
services/assess_service.py and routers/paths.py in place of
config.app_settings.AI_ENABLED.
"""

import json
import os
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SETTINGS_PATH = os.path.join(ROOT, "src", "data", "settings.json")

_CACHE: dict = {}
_LOCK = threading.Lock()


def _write() -> None:
    """Atomically serialize _CACHE to SETTINGS_PATH (temp file + os.replace).

    Callee of _load (seeding) and set_setting; callers hold _LOCK for
    writes except the one-time seed path which is inherently single-flight.
    """
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    tmp = f"{SETTINGS_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(_CACHE, fh, indent=2)
    os.replace(tmp, SETTINGS_PATH)


def _load() -> None:
    """Populate _CACHE from disk, seeding from env when the file is absent.

    Callee of get_setting/is_ai_enabled; creates settings.json with
    {"ai_enabled": env AI_ENABLED} on first access and persists it via _write.
    """
    global _CACHE
    if _CACHE:
        return
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
            _CACHE = json.load(fh) or {}
    else:
        _CACHE = {"ai_enabled": os.getenv("AI_ENABLED", "false").lower() == "true"}
        _write()


def get_setting(key, default=None):
    """Return a stored setting, loading from disk on first access.

    Called by routers/admin.py and callers needing non-boolean settings;
    delegates to _load then _CACHE.get with a fallback default.
    """
    _load()
    return _CACHE.get(key, default)


def set_setting(key, value) -> None:
    """Update one setting in memory and persist it atomically.

    Called by set_ai_enabled and routers/admin.py; loads, then under _LOCK
    mutates _CACHE[key] and writes via _write.
    """
    _load()
    with _LOCK:
        _CACHE[key] = value
        _write()


def is_ai_enabled() -> bool:
    """Return the runtime AI-enabled flag, seeded from env when unset.

    Called by routers/ai.py, services/llm_engine.py, services/assess_service.py
    and routers/paths.py in place of config.app_settings.AI_ENABLED.
    """
    _load()
    return bool(get_setting("ai_enabled", False))


def set_ai_enabled(value: bool) -> None:
    """Toggle the runtime AI-enabled flag and persist it to disk.

    Called by routers/admin.py PUT /api/admin/feature-flags; delegates to
    set_setting with a coerced boolean value.
    """
    set_setting("ai_enabled", bool(value))


def get_all() -> dict:
    """Return the raw stored settings dict, seeding from disk first.

    Called by settings_schema.build_runtime_flags and consumers needing the
    persisted store; delegates to _load then returns a shallow copy so
    callers cannot mutate the module-level _CACHE.
    """
    _load()
    return dict(_CACHE)


def reset_cache() -> None:
    """Clear the in-memory _CACHE so a changed SETTINGS_PATH takes effect.

    Called by tests for isolation (each suite reseeds from a fresh path);
    mirrors the _LOCK discipline used by set_setting.
    """
    with _LOCK:
        _CACHE.clear()
