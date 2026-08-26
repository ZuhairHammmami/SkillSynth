# SS-EDS: Events

## Purpose
Document the SSE event system: the in-memory pub/sub bus (`src/backend/events/publisher.py`), the exact event types and payloads emitted today, connection lifecycle, and the activity_log persistence used by the admin feed.

## Responsibilities
- Publish typed events to per-user queues via `send_event(profile_id, event_type, data)`
- Stream user frames (GET /api/realtime/events, alias /api/events) and the admin channel (GET /api/realtime/admin/events)
- Keep streams alive with 30s pings
- Persist auditable actions to activity_log

## Inputs
- Path generation success (routers/paths.py)
- Assessment submission success (routers/assessments.py)
- SS-AI job completion/failure and bounded review (routers/ai.py, services/assess_service.py — ADR-015)
- Client connect/disconnect lifecycle

## Outputs
- text/event-stream JSON frames
- activity_log rows consumed by GET /api/admin/events and the admin audit page

## Dependencies
- 07-backend (publisher.py, routers/realtime.py)
- 08-frontend (shared/hooks/useSSE.ts consumer)
- 22-api (stream endpoints)

## Sequence: Publish Flow
```
POST /api/generate-path/ succeeds
  → send_event(user_id, "path_generated", {"path_id": <id>})     # routers/paths.py:32
  → frame queued for that profile_id
  → event_generator yields data: {"type":"path_generated","data":{"path_id":...}}
  → useSSE invalidates React Query path keys
```

## State Diagram: Event Queue Lifecycle
```
[Connect] → [Queue registered] → [Frames yielded as they arrive]
                 ↓ idle 30s                    ↓ disconnect
            [ping keepalive]            [Queue removed in finally block]
```

## Event Catalog (complete — verified in code)
| Type | Emitter | Payload |
|------|---------|---------|
| connected | publisher.py generators | none |
| ping | publisher.py keepalive | none |
| path_generated | routers/paths.py:32 | {"path_id": int} |
| assessment_completed | routers/assessments.py:87 | {"assessment_id", "score", "total_questions"} |
| ai_quiz_ready | routers/ai.py | {"job_id", "questions": [...]} |
| ai_quiz_failed | routers/ai.py | {"job_id", "error"} |
| ai_test_ready | routers/ai.py | {"job_id", "assessment_id", "skill_id"} |
| ai_test_failed | routers/ai.py | {"job_id", "error"} |
| proficiency_adjusted | services/assess_service.py | {"skill_id", "skill_name", "delta", "rationale"} |

Admin channel frames mirror activity_log entries and honor the `?category=` filter on /api/realtime/admin/events.

Historical note (one line): gamification, notification, and broadcast event families were removed with their features; the four base types above plus the five SS-AI types (ADR-015) are all that is emitted.

## Publishing Pattern
```python
from backend.events.publisher import send_event, event_clients, admin_event_clients
send_event(profile_id, "assessment_completed",
           {"assessment_id": 3, "score": 80, "total_questions": 5})
```
Events fire only AFTER the database write succeeds.

## Heartbeat Mechanism
- `asyncio.wait_for(queue.get(), timeout=30)` inside both generators
- Timeout yields `{"type": "ping"}`; clients ignore it but proxies keep the socket open

## Persistence Boundary
- The pub/sub bus is memory-only: no replay, no dead-letter, no delivery guarantee
- Durable history lives in activity_log (category ∈ {audit, auth, system, learning, realtime}, JSON `data` column) — written via repositories, read through GET /api/admin/events

## Rules
1. One asyncio.Queue per (user, stream); multiple tabs are independent consumers
2. Full queue drops the new event (warning logged); clients recover by refetching after reconnect
3. New event types must be emitted from a router/service AND added to this catalog and 12-realtime
4. SSE auth uses Bearer or the 5-minute sse-token query parameter

## Edge Cases
- Token expiry mid-stream → current stream continues; reconnects need a fresh token
- Server restart clears all queues → EventSource auto-reconnect restores flow

## Failure Cases
- Slow client → bounded queue drops frames instead of blocking publishers
- Admin feed gaps → poll GET /api/admin/events for missed history (bus is not durable)

## Recovery Procedures
1. Reconnect with a fresh sse-token from POST /api/auth/sse-token
2. After reconnect, refetch affected queries rather than relying on missed events
