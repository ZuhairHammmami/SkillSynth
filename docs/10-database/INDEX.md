# SS-EDS: Database

## Purpose
Document the 15-domain-table strict-3NF schema, its canonical DDL (`src/migrations/003_reduced_schema.sql`), the ORM/DDL verifier, seed process, cascade and integrity policies for SkillSynth. Migration strategy = canonical DDL + verifier; no migration framework exists.

## Responsibilities
- Keep 15 tables in strict 3NF; JSON columns limited to the 4 documented exceptions (assessment_questions.options, path_steps.resource_ids/assessment_ids, activity_log.data)
- Keep DDL and ORM entities in sync — `PYTHONPATH=src python tools/verify_schema.py` prints SCHEMA MATCH
- Maintain 26 indexes (FK lookups, auth, time-range queries)
- Seed all tables idempotently via seed_v3.py
- Enforce FK cascade policy: CASCADE for ownership, SET NULL for optional references

## Inputs
- Domain model (05-domain)
- Query patterns from services/repositories

## Outputs
- Canonical DDL (src/migrations/003_reduced_schema.sql)
- Verdict from tools/verify_schema.py (tables/columns/PKs/FKs/ON DELETE/uniques)
- Seeded dev database (skillsynth.db)

## Dependencies
- 07-backend (ORM entities in entities/)
- 06-architecture (SQLite dev / PostgreSQL prod strategy)
- 11-learning-engine (prerequisite graph queries)

## Sequence: Database Mode Selection
```
Application start → read MODE → MODE=dev? → SQLite (skillsynth.db), check_same_thread=False
                                   ↓ no
                            PostgreSQL via DATABASE_URL (pooled: DB_POOL_SIZE,
                            DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, pool_pre_ping=True)
→ lifespan create_all (15 tables) → auto-create admin when ADMIN_PASSWORD set
```

## State Diagram: Schema Change Flow
```
[Edit ORM entity] → [Update 003_reduced_schema.sql] → [verify_schema.py]
        ↑                                                  ↓ mismatch
        └────────────── fix until SCHEMA MATCH ←──────────┘
```

## ERD References
- docs/40-diagrams/ERD.md — full diagram of the 15 tables

## Table Families
| Family | Tables |
|--------|--------|
| Identity | users |
| Catalog | categories, skills, skill_prerequisites, job_roles, job_role_skills, resources |
| Assessment | assessments, assessment_questions, assessment_results, user_skills |
| Learning | paths, path_steps, step_progress |
| Engagement | activity_log |

Junction tables: skill_prerequisites (prerequisite DAG) and job_role_skills (role→skill weighting). All M:N relationships use junction tables.

## Rules
1. seed_v3.py is the single authoritative seed (~1,100 rows, idempotent, FK-gated with PRAGMA foreign_key_check)
2. JSON columns only in the 4 documented exceptions
3. ON DELETE: CASCADE on ownership edges, SET NULL on optional references (13 CASCADE + 6 SET NULL clauses in DDL)
4. Soft delete: paths.deleted_at timestamp; queries filter deleted rows
5. Index every FK and frequently filtered column
6. Batch fetches only — no N+1 loops
7. Integrity enforcement: FK existence validated at service layer → 400; case-insensitive rename uniqueness on updates → 409; category parent cycles and prerequisite cycles → 400; centralized IntegrityError handler → 409

## Restricted Deletes
skills / categories / job_roles DELETE endpoints return **409 with a dependent-row census** unless `?force=true` is passed (documented in docs/41-decision-records/adr-014.md).

## Seed Coverage Policy
```bash
PYTHONPATH=src python seed_v3.py          # populates all 15 tables (~1,100 rows)
PYTHONPATH=src python tools/verify_schema.py   # → SCHEMA MATCH
```

## Examples
- Junction pattern: skill_prerequisites (skill_id, prerequisite_id)
- Cascade: deleting a user cascades to paths, step_progress, user_skills, assessment_results and nulls activity_log references per DDL

## Edge Cases
- SQLite vs PostgreSQL dialect differences (AUTOINCREMENT, timestamp precision)
- Self-referencing categories.parent_id hierarchy — cycle creation rejected at API level (400)

## Failure Cases
- SQLite file locked by another process → connection error
- PostgreSQL unreachable with MODE=prod → hard startup failure (no fallback by design)

## Recovery Procedures
1. Delete skillsynth.db and re-run `PYTHONPATH=src python seed_v3.py`
2. Check DATABASE_URL format and reachability for PostgreSQL
3. Apply schema manually from 003_reduced_schema.sql if recreating a prod database

## Refactoring Strategy
- Schema truth remains DDL + ORM + verifier; adopting a migration tool would require an ADR
- Add indexes based on observed query plans, verified against both dialects
