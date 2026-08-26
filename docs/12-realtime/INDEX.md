# SS-EDS: Realtime

## Purpose
Document the realtime infrastructure: unidirectional SSE (Server-Sent Events) streams for authenticated users and an admin channel, backed by an in-memory pub/sub bus (`src/backend/events/publisher.py`). SSE is the only push transport in the system.

## Responsibilities
- Stream events to a user at GET /api/realtime/events and the alias GET /api/events
- Stream admin-channel frames at GET /api/realtime/admin/events (optional category filter)
- Keep connections alive with 30s pings; drop queues on disconnect
- Expose `send_event(profile_id, event_type, data)` as the single publish API

## Inputs
- Path generation success → emits path_generated (routers/paths.py)
- Assessment submission success → emits assessment_completed (routers/assessments.py)
- Connection lifecycle of each client

## Outputs
- text/event-stream responses with JSON `data:` frames
- React Query invalidation on the client via shared/hooks/useSSE.ts

## Dependencies
- 07-backend (publisher.py, routers/realtime.py)
- 08-frontend (useSSE consumer)

## Sequence: SSE Connection Lifecycle
```
Client → POST /api/auth/sse-token (5-min SSE JWT, type=sse)
  → GET /api/realtime/events?token=<sse_token>
  → Server validates token, resolves profile_id
  → Registers per-user asyncio.Queue in event_clients[profile_id]
  → Yields {"type": "connected"}
  → On publish: send_event() puts frame on queue → yielded to client
  → Idle 30s: yields {"type": "ping"}
  → Disconnect: finally-block removes the queue
```

## State Diagram: Connection States
```
[Connecting] → [Connected] → [Receiving] ─┬─→ [Disconnected] → [Reconnect (new token)]
                 │              ↓          │
              [Auth Failed (401)]     [Ping keepalive every 30s idle]
```

## Emitted Event Types (complete list — verified in code)
| Event | Source | Payload |
|-------|--------|---------|
| connected | publisher.py generators | none (connection confirmation) |
| ping | publisher.py keepalive | none (30s idle heartbeat) |
| path_generated | routers/paths.py:32 | {"path_id": <id>} |
| assessment_completed | routers/assessments.py:87 | {"assessment_id", "score", "total_questions"} |
| ai_quiz_ready / ai_quiz_failed | routers/ai.py | {"job_id", "questions"} / {"job_id", "error"} |
| ai_test_ready / ai_test_failed | routers/ai.py | {"job_id", "assessment_id", "skill_id"} / {"job_id", "error"} |
| proficiency_adjusted | services/assess_service.py | {"skill_id", "skill_name", "delta", "rationale"} |

The admin channel (/api/realtime/admin/events) forwards activity_log-shaped frames and supports `?category=` filtering.

## Rules
1. Token auth accepts Bearer header or `token` query parameter (5-min SSE token recommended)
2. One asyncio.Queue per connected user per stream; multiple tabs = independent queues
3. Events are fire-and-forget — no persistence, replay, or delivery guarantee
4. Queue overflow drops the event (warning logged); clients recover by refetching
5. Heartbeat ping after any 30s idle window keeps proxies/NAT from closing the stream

## Examples
- Wizard completes → send_event(user_id, "path_generated", {"path_id": 42}) → frontend invalidates path queries
- Assessment submit → assessment_completed frame with score payload → analytics queries refresh

## Edge Cases
- SSE token expires mid-stream → existing stream continues; new connections need a fresh token
- Server restart → all in-memory queues vanish; clients auto-reconnect via EventSource

## Failure Cases
- Invalid/expired token on connect → HTTP 401 before streaming starts
- Slow consumer → bounded queue drops frames rather than blocking publishers

## Recovery Procedures
1. Client: EventSource auto-reconnects; fetch a new sse-token if 401 persists
2. After reconnect, React Query refetches active queries for full state sync

## Refactoring Strategy
- Multi-process deployments would require extracting the bus (Redis pub/sub) — needs an ADR first
- New event types must be added here and to 23-events together
