# SS-EDS: Release Notes

## Purpose
Record shipped changes with their breaking effects and migration steps. History is chronological, newest first; older entries are kept for context but link to the ADRs that superseded their world-view.

## Responsibilities
- Log each release's scope, breaking changes, and migration commands (real ones only)
- Link decisions to docs/41-decision-records/
- Flag credential/security follow-ups that survive releases

## Inputs
- Merged commit history and task reports (.superpowers/sdd/)
- ADRs (ADR-011, ADR-013; ADR-014 in progress)

## Outputs
- This changelog

## Dependencies
- 29-roadmaps (current queue)
- 42-runbooks (commands cited here must exist there)

## 2026-08 — Integrity Layer & 15-Table Core Completion
**Date**: 2026-08-25 · **Status**: Released
### Scope
- Schema reduced to a strict-3NF **15-table core**; canonical DDL src/migrations/003_reduced_schema.sql verified by tools/verify_schema.py (ADR-013)
- Admin CRUD completed: PUT users/skills/resources; categories & job-roles full CRUD; assessments list/delete
- Referential-integrity layer: unknown-FK → 400, rename conflicts → 409, prerequisite/category cycles → 400, IntegrityError net → 409 (services/catalog_integrity.py, main.py handler)
- Restricted deletes: DELETE skills/categories/job-roles with dependents → **409 + dependent counts** unless ?force=true (ADR-014)
- Removed features finalized: gamification, notifications, sessions table, granular roles, vector search, email service, socket-push transport (SSE is the only channel)
- Docs truth pass: SS-EDS sections rewritten to code reality; stale sections/files deleted
### Breaking Changes
- API surface rebuilt around 15 tables; clients of removed endpoints/features have no migration path (full rebuild documented across SS-EDS)
- Access token fixed at 24h; refresh endpoint does not exist
### Migration
```bash
rm skillsynth.db && PYTHONPATH=src python seed_v3.py   # fresh 15-table DB (~1100 rows)
PYTHONPATH=src python tools/verify_schema.py           # expect SCHEMA MATCH
PYTHONPATH=src python -m pytest tests/ -q              # expect 190 passed
```
**Security follow-up**: .env and src/frontend/.env.local hold live credentials — rotation still pending.

## Earlier Cycles (context only — superseded by ADR-013 where they conflict)
### Post-Rebuild Consolidation
- Dead layers removed (mappers/, validators/, later commands/queries/cache/infrastructure), isolated test DB introduced, separate admin app confirmed at src/admin-app (ADR-011 — superseded by ADR-013 on schema specifics)
### Performance Pass
- Inline 30s TTL cache on /api/public/stats, compression middleware ≥1KB bodies, batched queries replacing N+1 loops
### Assessment Engine & Analytics
- DB-backed assessment questions, submit scoring into user_skills (0–5), analytics dashboard/skill-growth/history endpoints
### Initial Build
- FastAPI + two Next.js apps (student :3000 ar/en RTL-first, admin :3001 English-only), JWT auth, SSE realtime, seeded catalog

## Release Format
```markdown
## YYYY-MM — Title
**Date**: YYYY-MM-DD · **Status**: Released
### Scope / ### Breaking Changes / ### Migration (+ commands) / ### Security follow-up
```

## Rules
1. Migration commands must be copy-runnable from the repo root today — stale commands get corrected, not archived as-is
2. Breaking changes name the ADR that authorized them
3. Security follow-ups stay listed until resolved, even across releases
4. Entries are append-only; corrections are made inline with a note

## Examples
- The 2026-08 entry cites only existing commands: seed_v3.py, tools/verify_schema.py, pytest

## Edge Cases
- Superseded entries remain for archaeology but never override newer truth

## Failure Cases
- Release without notes → backfill within the same cycle

## Recovery Procedures
1. Wrong entry → correct inline; never delete history silently

## Refactoring Strategy
- When history exceeds one screen, move pre-2026 entries to an archive section at the bottom
