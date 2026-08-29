"""Realtime router — SSE streams for users and the admin feed.

Wires /api/realtime to the module-level pub/sub bus in events/publisher.py
(Task 2). Streams authenticate via a signed token (query param, Bearer
header, or authToken cookie) and are consumed by useSSE.ts EventSource.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.events.publisher import admin_event_generator, event_generator
from backend.services import settings_schema
from backend.services.auth_service import decode_token

router = APIRouter()

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _quiet() -> bool:
    """Resolve the live real_time_updates flag to a transport quiet toggle.

    Called by the two SSE handlers; when the flag is off the stream stays
    open but the generator drops data frames (quiet-but-open).
    """
    return not settings_schema.get_runtime_flag("real_time_updates")


def _extract_profile_id(request: Request, token: str | None) -> int:
    """Resolve a signed token (query/Bearer/cookie) to a user id or 401.

    Accepts the 24h access token (carries an integer `user_id`) and the
    5-minute SSE token (numeric `sub`), matching useSSE.ts which passes
    the authToken cookie value as ?token=.
    """
    raw = token or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not raw:
        raw = request.cookies.get("authToken", "")
    if not raw:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(raw)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    if user_id is None:
        sub = payload.get("sub")
        if sub is None or not str(sub).isdigit():
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(sub)
    return int(user_id)


@router.get("/events")
async def sse_events(request: Request, token: str | None = None):
    """Stream one user's SSE frames from their personal queue. Calls
    publisher.event_generator; consumed by useSSE.ts (?token=)."""
    profile_id = _extract_profile_id(request, token)
    return StreamingResponse(event_generator(profile_id, quiet=_quiet()),
                             media_type="text/event-stream", headers=_SSE_HEADERS)


@router.get("/admin/events")
async def admin_sse_events(request: Request, token: str | None = None):
    """Stream the shared admin-channel SSE feed. Calls
    publisher.admin_event_generator; consumed by useSSE.ts (isAdmin)."""
    _extract_profile_id(request, token)
    return StreamingResponse(admin_event_generator(quiet=_quiet()),
                             media_type="text/event-stream", headers=_SSE_HEADERS)
