"""Feature-flag schema registry + validation (single source of truth).

Declares the authoritative FLAG_SCHEMA for the app's 13 feature flags,
resolves each flag's effective (runtime) value, and validates bulk update
payloads. Browse/edit feature flags only through this module; it is the ONLY
module that knows the 13 keys and their bounds.

Consumers: routers/admin.py (GET feature-flags, GET schema, PUT feature-flags)
and downstream runtime readers for the live flags (auth, realtime, limiter).
This module reads from backend.config.app_settings for env-derived defaults
and from backend.services.settings_service for persisted editable keys.
It never writes; persistence stays in settings_service (generic file store).

Callers of get_runtime_flag / build_runtime_flags: routers + runtime readers.
Callers of validate_update: the admin PUT handler (wired in Task 3).
"""

from backend.config import app_settings as settings
from backend.services import settings_service

# Per-key metadata: {type, editable, live, restart, default, min?, max?,
# min_length?, max_length?}. "editable:false" keys resolve from runtime env.
FLAG_SCHEMA: dict[str, dict] = {
    "app_mode": {
        "type": "str",
        "editable": False,
        "live": False,
        "restart": False,
        "default": settings.APP_MODE,
    },
    "registration_enabled": {
        "type": "bool",
        "editable": True,
        "live": True,
        "restart": False,
        "default": True,
    },
    "ai_enabled": {
        "type": "bool",
        "editable": True,
        "live": True,
        "restart": False,
        "default": settings.AI_ENABLED,
    },
    "ai_path_generation": {
        "type": "bool",
        "editable": False,
        "live": False,
        "restart": False,
        "default": settings.AI_ENABLED,
    },
    "ai_local_model": {
        "type": "str",
        "editable": True,
        "live": False,
        "restart": True,
        "min_length": 1,
        "max_length": 200,
        "default": settings.AI_MODEL_PATH,
    },
    "real_time_updates": {
        "type": "bool",
        "editable": True,
        "live": True,
        "restart": False,
        "default": True,
    },
    "csrf_protection": {
        "type": "bool",
        "editable": False,
        "live": False,
        "restart": False,
        "default": settings.CSRF_ENABLED,
    },
    "rate_limiting": {
        "type": "bool",
        "editable": True,
        "live": True,
        "restart": False,
        "default": True,
    },
    "password_policy": {
        "type": "object",
        "editable": True,
        "live": True,
        "restart": False,
        "default": {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digit": True,
            "require_special_char": True,
        },
    },
    "session_timeout_hours": {
        "type": "int",
        "editable": True,
        "live": True,
        "restart": False,
        "min": 1,
        "max": 168,
        "default": 24,
    },
    "account_lockout_attempts": {
        "type": "int",
        "editable": True,
        "live": True,
        "restart": False,
        "min": 1,
        "max": 10,
        "default": 5,
    },
    "lockout_minutes": {
        "type": "int",
        "editable": True,
        "live": True,
        "restart": False,
        "min": 1,
        "max": 1440,
        "default": 15,
    },
    "cors_origins": {
        "type": "list[str]",
        "editable": True,
        "live": False,
        "restart": True,
        "min_length": 0,
        "max_length": 20,
        "default": settings.CORS_ORIGINS,
    },
}

_BOOL_PASSWORD_KEYS = (
    "require_uppercase",
    "require_lowercase",
    "require_digit",
    "require_special_char",
)


def get_runtime_flag(key: str):
    """Return the effective value of a single flag.

    For editable keys the persisted setting (settings_service) overrides the
    schema default; for read-only keys the runtime env value is returned.
    Called by runtime readers (auth, realtime, limiter) and internally by
    build_runtime_flags so merge logic lives only here.
    """
    meta = FLAG_SCHEMA[key]
    if not meta["editable"]:
        if key == "ai_path_generation":
            return get_runtime_flag("ai_enabled")
        return meta["default"]
    return settings_service.get_setting(key, meta["default"])


def build_runtime_flags() -> dict:
    """Return the flat 13-key runtime flag map for GET /admin/feature-flags.

    Called by routers/admin.py; produces one entry per FLAG_SCHEMA key with
    value types identical to the current handler contract.
    """
    return {key: get_runtime_flag(key) for key in FLAG_SCHEMA}


def _validate_bool(value, key: str, errors: dict) -> bool:
    """Type-check a bool-typed flag value; record an error and return validity.

    Callee of validate_update; rejects non-bool values (booleans are not
    coerced from ints/strings), appending a message to errors.
    """
    if not isinstance(value, bool):
        errors[key] = f"Flag '{key}' must be a boolean."
        return False
    return True


def _validate_int(value, key: str, errors: dict) -> bool:
    """Type- and range-check an int-typed flag value.

    Callee of validate_update; rejects bool and non-int values plus values
    outside the min/max bounds, appending messages to errors.
    """
    meta = FLAG_SCHEMA[key]
    if isinstance(value, bool) or not isinstance(value, int):
        errors[key] = f"Flag '{key}' must be an integer."
        return False
    if "min" in meta and value < meta["min"]:
        errors[key] = f"Flag '{key}' must be at least {meta['min']}."
        return False
    if "max" in meta and value > meta["max"]:
        errors[key] = f"Flag '{key}' must be at most {meta['max']}."
        return False
    return True


def _validate_str(value, key: str, errors: dict) -> bool:
    """Type-, length- and whitespace-check a str-typed flag value.

    Callee of validate_update; enforces the 1..200 char bounds and rejects
    values containing any internal whitespace (e.g. ai_local_model).
    """
    meta = FLAG_SCHEMA[key]
    if not isinstance(value, str):
        errors[key] = f"Flag '{key}' must be a string."
        return False
    if len(value) < 1 or len(value) > 200:
        errors[key] = f"Flag '{key}' must be between 1 and 200 characters."
        return False
    if any(ch.isspace() for ch in value):
        errors[key] = f"Flag '{key}' cannot contain whitespace."
        return False
    return True


def _validate_cors_origins(value, key: str, errors: dict) -> bool:
    """Validate the cors_origins list-of-URLs value.

    Callee of validate_update; enforces 0..20 items, each a 1..200 char string
    beginning http:// or https://, appending messages to errors.
    """
    if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
        errors[key] = "Flag 'cors_origins' must be a list of strings."
        return False
    if len(value) > 20:
        errors[key] = "Flag 'cors_origins' must contain at most 20 items."
        return False
    for origin in value:
        if len(origin) < 1 or len(origin) > 200:
            errors[key] = "Each cors_origins entry must be 1-200 characters."
            return False
        if not (origin.startswith("http://") or origin.startswith("https://")):
            errors[key] = "Each cors_origins entry must start with http:// or https://."
            return False
    return True


def _validate_password_policy(value, errors: dict) -> bool:
    """Validate provided password_policy sub-keys.

    Callee of validate_update; requires a dict and validates any provided
    sub-keys (min_length int 6..32; the four require_* bools). Missing
    sub-keys are allowed (existing stored/default values are kept).
    """
    if not isinstance(value, dict):
        errors["password_policy"] = "Flag 'password_policy' must be an object."
        return False
    if "min_length" in value:
        if isinstance(value["min_length"], bool) or not isinstance(value["min_length"], int):
            errors["password_policy"] = "password_policy.min_length must be an integer."
            return False
        min_len = value["min_length"]
        if min_len < 6 or min_len > 32:
            errors["password_policy"] = "password_policy.min_length must be between 6 and 32."
            return False
    for sub_key in _BOOL_PASSWORD_KEYS:
        if sub_key in value and not isinstance(value[sub_key], bool):
            errors["password_policy"] = f"password_policy.{sub_key} must be a boolean."
            return False
    return True


def validate_update(payload: dict) -> tuple[dict, dict]:
    """Validate a bulk feature-flag update payload -> (cleaned, errors).

    Called by the admin PUT handler. Each payload key is validated per its
    schema; errors map key->message. cleaned holds only validation-passing
    keys (partial on error); callers persist only when errors is empty.
    """
    cleaned: dict = {}
    errors: dict = {}
    for key, value in payload.items():
        if key not in FLAG_SCHEMA:
            errors[key] = f"Unknown flag '{key}'."
            continue
        meta = FLAG_SCHEMA[key]
        if not meta["editable"]:
            errors[key] = f"Flag '{key}' is read-only."
            continue
        flag_type = meta["type"]
        if flag_type == "bool":
            if not _validate_bool(value, key, errors):
                continue
        elif flag_type == "int":
            if not _validate_int(value, key, errors):
                continue
        elif flag_type == "str":
            if not _validate_str(value, key, errors):
                continue
        elif flag_type == "list[str]":
            if not _validate_cors_origins(value, key, errors):
                continue
        elif flag_type == "object":
            if not _validate_password_policy(value, errors):
                continue
        cleaned[key] = value
    return cleaned, errors
