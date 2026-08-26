"""Shared service-error → HTTP-status mapping for the admin routers.

Consumed by routers/admin.py and routers/catalog_admin.py so every
service error string maps to one REST status consistently:
'*not found*' → 404, uniqueness/restricted-delete/demotion conflicts →
409, everything else (unknown references, cycles, bad shapes) → 400.
"""

_CONFLICT_MARKERS = ("already exists", "already registered", "in use", "demote")


def status_for_error(error: str | dict) -> int:
    """Map a service error payload onto its HTTP status code.

    Called by every catalog/admin write handler right before raising;
    dict payloads are structured restricted-delete conflicts
    ({dependents, message}) and always mean 409.
    """
    if isinstance(error, dict):
        return 409
    lowered = error.lower()
    if "not found" in lowered:
        return 404
    if any(marker in lowered for marker in _CONFLICT_MARKERS):
        return 409
    return 400
