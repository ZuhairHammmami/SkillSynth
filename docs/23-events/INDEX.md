# SS-EDS: Events

## Purpose
Document the real-time event system — SSE (Server-Sent Events) streams for live progress updates, analytics refresh, and admin monitoring, backed by activity_log and the in-memory pub/sub bus.

## Responsibilities
- Broadcast real-time events to users (SSE) and admins (admin SSE stream)
- Maintain per-user event queues with 30s heartbeat (ping)
- Persist audit events to events table via EventService
- Provide publisher API (EventPublishers) for 7+ event types

## Inputs
- User actions (step completion, assessment submission)
- System events (path generation, admin actions)
- ~~Gamification triggers (XP, achievements)~~, streaks (streaks retained)

## Outputs
- SSE event stream (backend → frontend, per-user)
- Admin event stream (backend → admin dashboard)
- Audit log entries (events table + JSON logger)

## Dependencies
- 07-backend (events/publisher.py, services/sse_service.py, services/event_service.py)
- 08-frontend (EventSource connection, React Query invalidation)
- 22-api (SSE endpoint at /api/realtime/events)

## Sequence: SSE Connection Flow
```
Client → POST /api/auth/sse-token (get 5-min SSE JWT)
  → GET /api/realtime/events?token=<sse_token>
  → Server creates asyncio.Queue per profile_id
  → Yields "connected" event
  → 30s heartbeat: {"type": "ping"}
  → On event: yield "data: {json}\n\n"
  → On disconnect: clean up queue
```

## State Diagram: Event Queue Lifecycle
```
[Client Connects] → [Queue Created] → [Heartbeat (30s)] → [Event Pushed] → [Event Sent]
                                        ↓                       ↓
                                   [Ping Keepalive]      [Queue Full → Drop, Log]
                                        ↓
                              [Client Disconnects] → [Queue Removed]
```

## Event Catalog (7 primary SSE types + 6 secondary)

| Event Type | Source | Payload | Trigger |
|------------|--------|---------|---------|
| progress_update | SSEService | path_id, completed_steps, total_steps, percentage | Step completed |
| ~~xp_update~~ | ~~SSEService~~ | ~~xp_earned, total_xp, level, xp_for_next~~ | **REMOVED** |
| notification | SSEService | title, message, type | System notification |
| analytics_refresh | SSEService | {} | Data mutation |
| system_alert | SSEService | level, message | System event |
| step_completed | SSEService | step_id, path_id, step_number, title, xp | User action |
| ~~achievement_unlocked~~ | ~~SSEService~~ | ~~achievement_type, data~~ | **REMOVED** |

### Secondary Events (via EventPublishers / events/publisher.py)
| Event Type | Publisher | Trigger |
|------------|-----------|---------|
| path_regenerated | send_event() | Path regeneration |
| step_reverted | send_event() | Step undo |
| assessment_completed | EventPublishers | Assessment submit |
| xp_awarded | EventPublishers | XP gained |
| path_updated | EventPublishers | Path mutation |
| connection_status | WebSocket | WS connect/disconnect |

## Event Publishing Pattern
```python
# Direct publish via send_event (events/publisher.py):
send_event(profile_id, "step_completed", {"step_id": 1, "xp": 10})

# Via SSEService (services/sse_service.py):
SSEService.broadcast_to_user(profile_id, "progress_update", data)
SSEService.broadcast_to_admins("system_alert", {"level": "info", "message": "..."})

# Via EventPublishers (events/publishers.py):
EventPublishers.publish_step_completed(profile_id, step_id, path_id, ...)
# ~~publish_xp_gained, publish_achievement_unlocked~~ REMOVED
```

## Heartbeat Mechanism
- 30-second timeout on asyncio.wait_for()
- Timeout yields `{"type": "ping"}` keepalive
- Client ignores ping events, only processes typed events
- Prevents proxy/NAT connection drops

## Event Persistence
```python
# EventService.log_event() writes to events table:
# profile_id, category, action, entity_type, entity_id, data (JSON), ip_address
EventService.log_event(db, profile_id=1, category="learning",
    action="step_completed", entity_type="step", entity_id=5,
    data={"xp_awarded": 10})
```

## Rules
1. Events fire AFTER DB write completes
2. Per-user queue capped — full queue drops messages silently
3. Heartbeat every 30s — no event for 30s triggers ping
4. Admin events broadcast to all admin SSE clients
5. SSE token valid for 5 minutes only

## Edge Cases
- Rapid events from same user → queue accepts all, dropped only if full
- SSE token expires mid-stream → client reconnects with new token
- WebSocket disconnect → cleanup active_websockets dict

## Failure Cases
- Queue full → message dropped, warning logged
- SSE connection lost → client refetches via React Query
- Events table unbounded growth → archive old events

## Recovery Procedures
1. Check SSE connection health: verify EventSource open
2. Reconnect with fresh SSE token from /api/auth/sse-token
3. Clear stale queues via server restart
