# SS-EDS: Roadmaps

## Purpose
Track the current state of SkillSynth and the near-term work queue. Historical phase narratives (Phases 0–11) are closed; this document records what exists today and what is planned next.

## Responsibilities
- Maintain the current-state capability snapshot
- Define the active work queue (integrity layer, docs truth, hardening)
- Route completed history to 45-release-notes and decisions to 41-decision-records

## Inputs
- Commit history (git log)
- ADRs (docs/41-decision-records/)
- Test suite status (tests/, 142 passing)

## Outputs
- Current-state table (below)
- Prioritized backlog

## Dependencies
- 39-future (long-term vision)
- 45-release-notes (shipped history)
- 38-refactoring (debt process)

## Current State (August 2026)
| Area | State | Evidence |
|------|-------|----------|
| Backend | FastAPI Clean Architecture, 7 routers / 49 paths / 63 operations | src/backend/routers/, OpenAPI at :8000/docs |
| Database | Strict-3NF 15-table core + seed_v3 (~1100 rows) | src/migrations/003_reduced_schema.sql, tools/verify_schema.py → SCHEMA MATCH |
| Admin CRUD | Full users/skills/categories/resources/job-roles CRUD incl. restricted deletes | routers/admin.py, routers/catalog_admin.py |
| Integrity layer | FK validation 400, cycle guards 400, restricted deletes 409, IntegrityError→409 net | services/catalog_integrity.py, main.py:115 |
| Realtime | SSE only (connected/ping/path_generated/assessment_completed) | events/publisher.py, routers/realtime.py |
| Frontend | Next.js 14 student app :3000, bilingual ar/en, RTL-first | src/frontend/ |
| Admin app | Separate Next.js app :3001 with categories/job-roles pages | src/admin-app/ |
| Tests | 142 passing across 11 files, isolated temp DB | PYTHONPATH=src python -m pytest tests/ -q |

## Active Queue
| Item | Focus | Status |
|------|-------|--------|
| ADR-014 | Referential-integrity policy write-up (restricted deletes, force flag) | In progress |
| Docs truth pass | SS-EDS sections aligned to code reality; stale sections deleted | In progress |
| Credential rotation | .env and src/frontend/.env.local hold live credentials | Planned |

## Sequence: How Work Enters the Queue
```
Gap found (test failure, doc drift, review) → scoped as task in the SDD plan
  → implemented behind tests → verified (pytest + verify_schema + builds)
  → recorded here or in 45-release-notes if user-visible
```

## Rules
1. No resurrected features without an ADR (e.g., gamification stays deleted — see ADR-013)
2. Every roadmap item names its verification command before implementation starts
3. Completed items move to 45-release-notes within the same cycle
4. Schema changes always update the canonical DDL and pass tools/verify_schema.py

## Examples
- Restricted deletes shipped with a 409 dependent-counts payload plus ?force=true escape hatch — verified by tests/test_catalog_integrity.py
- 15-table reduction shipped with DDL + verifier as proof (ADR-013)

## Edge Cases
- Item spans backend+frontend → split into per-repo tasks with one integration test
- Verification impossible (pure docs) → grep gates replace pytest

## Failure Cases
- Roadmap drift (claims ahead of code) → corrected during docs truth passes like this one

## Recovery Procedures
1. Re-run the verification commands in the Current State table
2. Correct any row whose evidence fails

## Refactoring Strategy
- Keep this file short: history ages out to 45-release-notes, vision lives in 39-future
