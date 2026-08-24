"""In-memory SSE pub/sub bus (no persistence — events are fire-and-forget).

Two channels: per-user queues keyed by profile_id and a shared admin
queue. Routers stream from the generators; services publish via send_*.
"""

import json
import asyncio
from collections import defaultdict
from typing import AsyncGenerator

event_clients: dict[int, list] = defaultdict(list)
admin_event_clients: list = []


async def admin_event_generator(category: str | None = None) -> AsyncGenerator[str, None]:
    """Stream admin-channel SSE frames, optionally filtered by category.

    Consumed by GET /admin/events/stream; publishes arrive through
    send_admin_event. Emits `connected` then pings every 30s.
    """
    queue: asyncio.Queue = asyncio.Queue()
    admin_event_clients.append(queue)
    try:
        yield "data: {\"type\": \"connected\"}\n\n"
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=30)
                if category and data.get("category") and data["category"] != category:
                    continue
                yield f"data: {json.dumps(data)}\n\n"
            except asyncio.TimeoutError:
                yield "data: {\"type\": \"ping\"}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if queue in admin_event_clients:
            admin_event_clients.remove(queue)


def send_admin_event(event_data: dict):
    """Fan one payload out to every connected admin stream.

    Called by admin activity logging to mirror persisted rows into
    open /admin/events/stream connections; silently drops on full
    queues so slow clients never block writers.
    """
    for queue in admin_event_clients:
        try:
            queue.put_nowait(event_data)
        except asyncio.QueueFull:
            pass


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
