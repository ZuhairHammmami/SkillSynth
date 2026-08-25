# SS-EDS: Realtime

## Purpose
Document the real-time event infrastructure using SSE (Server-Sent Events) and WebSocket, connection manager with per-user broadcasting, heartbeat (30s), event type catalog, and React Query integration for live updates.

## Responsibilities
- Stream real-time events to authenticated clients via SSE at GET /api/realtime/events
- Manage WebSocket connections at /ws with subscribe/unsubscribe protocol
- Maintain per-user connection pools with queue-based broadcasting
- Handle connection lifecycle (connect, keepalive, reconnect, disconnect)
- Broadcast 12 event types to users and admin channels
- Provide admin notification endpoint at POST /api/realtime/notify

## Inputs
- Step completion events from progress_router.py
- Path generation events from paths_router.py
- Assessment completion events from assessments_router.py
- XP events from service layer
- System alerts from admin

## Outputs
- SSE stream at GET /api/realtime/events (text/event-stream)
- WebSocket connection at /ws (JSON message protocol)
- Real-time UI updates via React Query cache invalidation
- Admin broadcast via POST /api/realtime/broadcast

## Dependencies
- 07-backend (SSEService, publisher.py, realtime_router.py)
- 08-frontend (EventSource consumer in React Query hooks)
- 10-database (events table for audit trail)

## Sequence: SSE Connection Lifecycle
```
Client → GET /api/realtime/events (JWT auth via Bearer/cookie/query)
  → Server validates token → extracts profile_id
  → Creates per-user asyncio.Queue → appends to event_clients[profile_id]
  → Emits {"type": "connected"} confirmation
  → On user event: Server puts message on queue → client receives
  → Every 30s idle: Server sends {"type": "ping"} keepalive
  → On disconnect: Queue removed from event_clients → cleanup
```

## State Diagram: Connection States
```
[Connecting] → [Connected] → [Receiving] → [Disconnected]
       ↓           ↓              ↓               ↓
[Auth Failed]  [Heartbeat]  [Queue Full]    [Reconnect (backoff)]
```

## Sequence: WebSocket Protocol
```
Client → /ws (handshake)
  → Server accepts → awaits auth JSON {token: "..."}
  → Validates → sends {"type":"connection_status","status":"connected"}
  → Client sends {"type":"ping"} → Server responds {"type":"pong"}
  → Client sends {"type":"subscribe","channels":[...]} → Server acknowledges
  → Client sends {"type":"unsubscribe","channels":[...]} → Server acknowledges
  → On disconnect → cleanup active_websockets[profile_id]
```

## Event Types
| Event | Trigger | Payload |
|-------|---------|---------|
| progress_update | Step complete/revert | path_id, completed_steps, total_steps, percentage |
| ~~xp_update~~ | ~~XP earned~~ | ~~xp_earned, total_xp, level, xp_for_next~~ | **REMOVED** |
| notification | System or admin push | title, message, type |
| analytics_refresh | Analytics update | {} (trigger refetch) |
| system_alert | System event | level, message |
| step_completed | Step completion | profile_id, step_id, path_id |
| step_reverted | Step undo | profile_id, step_id, path_id |
| path_generated | Path generation | path_id |
| skill_progress_updated | Skill progress | skill_id, new_level |
| ~~achievement_unlocked~~ | ~~Achievement~~ | ~~achievement_type, title~~ | **REMOVED** |
| assessment_completed | Assessment | assessment_id, score |
| connection_status | Connection lifecycle | status, profile_id |

## Rules
1. Auth supports: Bearer token, query param token, or authToken cookie
2. Keepalive: 30s ping interval via asyncio.wait_for(timeout=30)
3. SSE uses queue-per-client with QueueFull dropping (logged warning)
4. WebSocket uses JSON protocol with typed messages (ping/pong/subscribe)
5. Admin events broadcast to all admin_event_clients

## Examples
- User completes step → SSEService.send_progress_update → SSE event → React Query invalidates path query → UI updates
- Multiple browser tabs → each has own SSE connection → independent queue

## Edge Cases
- Event queue overflow → message dropped with warning, client refetches on reconnect
- Network interruption → EventSource auto-reconnects, React Query refetches full state
- Server restart → all connections drop, clients reconnect with backoff

## Failure Cases
- Queue full for user → event dropped to prevent memory leak
- Invalid token on SSE → 401 HTTP response, client must re-auth
- WebSocket auth failure → {"type":"error"} message + close

## Recovery Procedures
1. Client-side: EventSource auto-reconnect with exponential backoff
2. After reconnect: React Query invalidates all active queries for full state sync
3. Server-side: stale connections cleaned on keepalive timeout (queue.get timeout)

## Refactoring Strategy
- Migrate from per-queue to Redis pub/sub for horizontal scaling
- Add event persistence with dead-letter queue for guaranteed delivery
- Implement channel-based authorization for admin SSE filtering
