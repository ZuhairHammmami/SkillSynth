import json
import asyncio
from collections import defaultdict
from typing import AsyncGenerator

event_clients: dict[int, list] = defaultdict(list)
admin_event_clients: list = []


async def admin_event_generator(category: str | None = None) -> AsyncGenerator[str, None]:
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
    for queue in admin_event_clients:
        try:
            queue.put_nowait(event_data)
        except asyncio.QueueFull:
            pass


async def event_generator(profile_id: int) -> AsyncGenerator[str, None]:
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
    if profile_id in event_clients:
        message = {"type": event_type, **(data or {})}
        for queue in event_clients[profile_id]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass
