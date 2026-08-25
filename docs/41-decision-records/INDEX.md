# SS-EDS: Decision Records (ADR)

## Purpose
Index the architectural decision records for SkillSynth. The directory contains only live decision documents; historical inventory reports were deleted during the 2026-08 cleanup.

## Responsibilities
- Record significant architecture decisions with context and consequences
- Track status (Proposed / Accepted / Superseded) and supersession chains

## Inputs
- Architecture discussions and review findings
- Schema/API changes requiring recorded rationale

## Outputs
- ADR files in this directory (adr-XXX.md)
- Decision table below

## Dependencies
- 06-architecture (decisions shape the architecture)
- 00-principles (decisions must align with principles)

## ADR Process
```
Identify Decision → Draft ADR → Review → Accept/Reject → Implement → Supersede via newer ADR when reversed
```

## Decision Table
| ADR | Title | Status | File |
|-----|-------|--------|------|
| ADR-001 | Dual-backend pattern (FastAPI + Next.js apps) | Accepted | not digitized |
| ADR-002 | SSE over second socket transport for realtime | Accepted | not digitized |
| ADR-003 | JWT access-only auth (24h), no refresh rotation | Accepted | not digitized |
| ADR-006 | SQLite dev / PostgreSQL prod mode switching | Accepted | not digitized |
| ADR-007 | Gamification as side effects | **Superseded by ADR-013** (gamification fully removed) | file never created; title preserved here |
| ADR-010 | Local-first LLM provider chain → static fallback | Accepted | not digitized |
| ADR-011 | Post-rebuild consolidation (dead layers removed, isolated tests, canonical DDL v2, separate admin app) | **Superseded by ADR-013** (schema specifics; operational points stand) | adr-011.md |
| ADR-013 | Feature reduction to the 15-table core (admin CRUD completion, integrity layer, removal of gamification/notifications/sessions/granular roles) — see [adr-013.md](adr-013.md) | Accepted | adr-013.md |
| ADR-014 | Referential-Integrity Policy (FK validation → 400, rename-uniqueness → 409, cycle guards → 400, restricted deletes with census payloads + ?force=true semantics) — see [adr-014.md](adr-014.md) | Accepted | adr-014.md |

## Template
```markdown
# ADR-XXX: Title
## Status   [Proposed | Accepted | Superseded by ADR-YYY]
## Context  What motivates this decision?
## Decision What is the chosen approach?
## Consequences  Trade-offs, costs, benefits?
## Options Considered
```

## Rules
1. One unique number per decision; numbers are never reused
2. A superseding ADR names its predecessor, and the predecessor's Status line is updated the same day
3. ADRs are immutable after acceptance except for the Status line
4. Only significant decisions get ADRs; trivia lives in commit messages

## Examples
- ADR-002 rationale: one-way event push suffices for connected/ping/path_generated/assessment_completed; no client→server stream needed

## Edge Cases
- Partially superseded ADRs (like ADR-011) state exactly which clauses survive

## Failure Cases
- Reversing a decision without an ADR → future contributors re-litigate settled ground

## Recovery Procedures
1. Missing ADR for shipped behavior → write it retrospectively, marked as such in Context

## Refactoring Strategy
- Digitize "not digitized" entries only when their rationale becomes load-bearing again
