# SS-EDS: Diagrams

## Purpose
Index the authoritative diagrams for SkillSynth and host the architecture/request-lifecycle sequences. The canonical ERD lives beside this file; everything else is inline ASCII in the owning section.

## Responsibilities
- Keep the diagram inventory pointing at existing, current documents
- Host Clean Architecture and request-lifecycle sequences
- Enforce "diagram matches code" during docs truth passes

## Inputs
- Canonical DDL src/migrations/003_reduced_schema.sql (15 tables)
- Router layout src/backend/routers/ (8 routers)
- SSE event set events/publisher.py

## Outputs
- ERD: docs/40-diagrams/ERD.md (Mermaid erDiagram)
- Sequences below (ASCII)

## Dependencies
- 10-database (schema truth for the ERD)
- 06-architecture (layer definitions mirrored here)

## Diagram Inventory
| Diagram | Location | Format |
|---------|----------|--------|
| ERD (15 tables) | docs/40-diagrams/ERD.md | Mermaid |
| System block diagram | docs/06-architecture/INDEX.md | ASCII |
| Backend startup state | docs/06-architecture/INDEX.md | ASCII |
| Learning engine data flow | docs/11-learning-engine/INDEX.md | ASCII |
| SSE connection lifecycle | docs/12-realtime/INDEX.md | ASCII |
| Request lifecycle | this file | ASCII |

## Sequence: Clean Architecture Request Lifecycle
```
Client → HTTP request
  → middleware stack (CORS → compression → security headers → CSRF [prod])
  → rate limiter (slowapi)
  → router (thin handler) → policy (get_current_user / require_admin)
    → service (business logic; integrity guards)
      → repository (SQLAlchemy queries)
        → entity/model → database
      ← ORM objects
    ← result tuple or domain dict
  ← JSON response (or text/event-stream on SSE endpoints)
```

## Sequence: Path Generation (current flow)
```
POST /api/generate-path/ (Bearer JWT)
  → wizard_service scores answers → user_skills upserts
  → learning_service._order_by_prereqs (topological sort of skill_prerequisites DAG)
  → _persist_plan creates path + ordered path_steps (+ resource_ids picks)
  → publish_sse("path_generated") to the user's stream if connected
  ← PathDetailOut
```
Sequence diagrams for removed flows (gamification awards, notification fan-out, second-socket channels) were pruned — no such flows exist.

## Transport Map (SSE is the only push transport)
| Channel | Endpoint | Auth |
|---------|----------|------|
| User SSE stream | GET /api/realtime/events (+ alias GET /api/events) | short-lived SSE token |
| Admin SSE channel | GET /api/realtime/admin/events | admin + SSE token |

## Rules
1. Diagrams are Mermaid (standalone .md) or ASCII (inline) — both version-controlled
2. Any schema/router change updates ERD.md and the affected inline diagram in the same PR
3. ERD keeps FK and ON DELETE annotations visible
4. A diagram referencing a removed feature is deleted, never annotated as historical

## Examples
- ERD snippet style: `users ||--o{ paths : "owns"` with cascade notes

## Edge Cases
- Mermaid renderers differ → validate on GitHub preview before merging
- 15-table ERD fits one diagram; sub-diagrams only if tables grow

## Failure Cases
- Stale diagram discovered → fix immediately; treat like a failing test

## Recovery Procedures
1. Re-derive the ERD from entities/*.py + DDL, then run python tools/verify_schema.py to confirm the baseline before editing

## Refactoring Strategy
- If tables grow past ~20, split ERD per entity family (identity/catalog/learning/assessment/engagement)
