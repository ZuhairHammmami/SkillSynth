# SS-EDS: Decision Records (ADR)

## Purpose
Document architectural decision records (ADRs) for SkillSynth. Captures significant architecture decisions, their context, consequences, and rationale.

## Responsibilities
- Record all significant architectural decisions
- Document decision context, options considered, and chosen approach
- Track decision status (proposed, accepted, deprecated, superseded)
- Provide rationale for future developers

## Inputs
- Architecture discussions
- Design reviews
- Performance/security findings

## Outputs
- ADR documents (doc/41-decision-records/adr-XXX.md)
- Decision log

## Dependencies
- 06-architecture (decision recording)
- 00-principles (decisions align with principles)

## Sequence: ADR Process
```
Identify Decision → Draft ADR → Review → Accept/Reject → Implement → Revisit if needed
```

## ADR Template
```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue motivating this decision?

## Decision
What is the chosen approach?

## Consequences
What are the trade-offs, costs, and benefits?

## Options Considered
1. Option A — pros/cons
2. Option B — pros/cons
```

## Key Architectural Decisions
| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Dual-backend pattern (FastAPI + Next.js) | Accepted |
| ADR-002 | SSE over WebSockets for real-time | Accepted |
| ADR-003 | JWT auth with 7-day expiry, no blacklist | Accepted (known gap) |
| ADR-004 | Flat solid colors, no gradients | Accepted |
| ADR-005 | RTL-first, Arabic-default | Accepted |
| ADR-006 | SQLite dev / PostgreSQL prod mode switching | Accepted |
| ADR-007 | Gamification as side-effects, not standalone | Accepted |
| ADR-008 | Static JSON files as legacy fallback | Accepted |
| ADR-009 | RBAC with 6 fixed roles | Accepted |
| ADR-010 | Local-first LLM (Ollama) → OpenAI → static fallback | Accepted |
| ADR-011 | Post-rebuild consolidation (dead layers removed, cache/scheduler wired, isolated test DB, canonical DDL, separate admin app) — see [adr-011.md](adr-011.md) | Accepted |
| ADR-013 | Feature reduction to 15-table core (RBAC/notifications/sessions dropped, 7-router API, divide-and-conquer code) — see [adr-013.md](adr-013.md) | Accepted |

## ERD References
- No ADR-specific database tables

## Rules
1. ADRs are written for significant decisions only (not trivial choices)
2. Each ADR has a unique number (ADR-XXX)
3. Status must be one of: Proposed, Accepted, Deprecated, Superseded
4. Superseded ADRs must reference the superseding ADR
5. ADRs are immutable once accepted (add new ADR to change)

## Examples
- ADR-002: "SSE over WebSockets" — simpler implementation, sufficient for event types (step_completed, step_reverted, etc.), no bidirectional communication needed

## Edge Cases
- Decision reversed after acceptance → new ADR supersedes old one
- Multiple decisions on same topic → latest status takes precedence
- Missing ADR for past decisions → retrospective documentation

## Failure Cases
- Not recording a decision → future developers don't know rationale
- ADR too vague → not useful for decision rationale
- ADR not reviewed → may contain errors

## Recovery Procedures
1. Document decision retroactively with available context
2. Link to related code changes and discussions
3. Seek team input for missing context

## Refactoring Strategy
- ~~Use ADR template CLI tool for consistent formatting~~ (CLI tool removed)
- Link ADRs to code via commit messages (ADR-XXX references)
- Regular ADR review for continued relevance
