"""In-memory SSE pub/sub bus (no persistence — events are fire-and-forget).

Two channels: per-user queues keyed by profile_id and a shared admin
queue. Routers stream from the generators; services publish via send_*.
Admin frames are emitted as named SSE events (`event: <type>`) so the
admin app's addEventListener(type, ...) subscriptions actually fire.
"""

import json
import asyncio
from collections import defaultdict
from typing import AsyncGenerator

event_clients: dict[int, list] = defaultdict(list)
admin_event_clients: list = []


async def admin_event_generator(category: str | None = None) -> AsyncGenerator[str, None]:
    """Stream admin-channel SSE frames, optionally filtered by category.

    Consumed by GET /admin/events/stream via routers/realtime. Frames use
    the named-event wire format (`event: <type>`) because the admin app
    subscribes with addEventListener(type, ...). Emits `connected` then
    pings every 30s.
    """
    queue: asyncio.Queue = asyncio.Queue()
    admin_event_clients.append(queue)
    try:
        yield "event: connected\ndata: {\"type\": \"connected\"}\n\n"
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=30)
                if category and data.get("category") and data["category"] != category:
                    continue
                yield f"event: {data['type']}\ndata: {json.dumps(data)}\n\n"
            except asyncio.TimeoutError:
                yield "event: ping\ndata: {\"type\": \"ping\"}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if queue in admin_event_clients:
            admin_event_clients.remove(queue)


async def event_generator(profile_id: int) -> AsyncGenerator[str, None]:
    """Stream one user's SSE frames from their personal queue.

    Consumed by GET /api/events after token auth resolves profile_id;
    publishes arrive through send_event. Pings keep proxies alive.
    """
    queue: asyncio.Queue = asyncio.Queue()
    event_clients[profile_id].append(queue)
    try:
        yield "data: {\"type\": \"connected\"}\n\n"
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
            except asyncio.TimeoutError:
                yield "data: {\"type\": \"ping\"}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if queue in event_clients[profile_id]:
            event_clients[profile_id].remove(queue)
        if not event_clients[profile_id]:
            del event_clients[profile_id]


def send_event(profile_id: int, event_type: str, data: dict | None = None):
    """Push {type, **data} to all live streams of one user.

    Called by assessment/learning flows (e.g. assessment_completed,
    path_generated); no-op when the user has no open stream.
    """
    if profile_id in event_clients:
        message = {"type": event_type, **(data or {})}
        for queue in event_clients[profile_id]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass


def send_admin_event(event_type: str, data: dict | None = None):
    """Push {type, **data} to every live admin-channel stream.

    Called alongside send_event where admin-visible events occur
    (path_generated, assessment_completed, activity); no-op when no
    admin has an open SSE stream. Swallows QueueFull like send_event.
    """
    message = {"type": event_type, **(data or {})}
    for queue in admin_event_clients:
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            pass


def send_admin_activity(row) -> None:
    """Broadcast an `activity` admin frame serialized from an activity_log row.

    Called by the audit write sites right after engagement_repository.write;
    the payload mirrors the /admin/events item keys so the admin audit-log
    feed can prepend the entry, and created_at becomes ISO like the feed.
    """
    frame = {
        "id": row.id,
        "category": row.category,
        "action": row.action,
        "user_id": row.user_id,
        "entity_type": row.entity_type,
        "entity_id": int(row.entity_id)
        if row.entity_id and str(row.entity_id).isdigit() else row.entity_id,
        "data": row.data or {},
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
    send_admin_event("activity", frame)
