# SS-EDS: Database

## Purpose
Document the 15-domain-table strict 3NF database schema, its canonical DDL (`src/migrations/003_reduced_schema.sql`, verified against the ORM by `tools/verify_schema.py` → SCHEMA MATCH), migration strategy, seed data process, cascade policies, and query optimization for SkillSynth.

## Responsibilities
- Maintain 15 domain tables in strict 3NF with JSON columns limited to the 4 documented exceptions (assessment_questions.options, path_steps.resource_ids/assessment_ids, activity_log.data)
- Keep the canonical DDL (`src/migrations/003_reduced_schema.sql`) in sync with ORM entities; verify with `python tools/verify_schema.py`
- Define evidence-driven indexes (17+ covering common query patterns)
- Manage seed data via seed_v3.py (authoritative source)
- Handle SQLite (dev) and PostgreSQL (prod) compatibility
- Enforce FK cascade policies (CASCADE for ownership, SET NULL for optional refs)
- Support soft delete via deleted_at timestamp on core tables

## Inputs
- Domain model definitions (05-domain)
- Performance requirements (04-non-functional-requirements)
- Data relationships from ERD (docs/40-diagrams/ERD.md)

## Outputs
- Canonical DDL (src/migrations/003_reduced_schema.sql)
- Schema verifier (tools/verify_schema.py — prints SCHEMA MATCH on success)
- Seed script (seed_v3.py)
- Migration scripts (src/migrations/*.sql)
- Query optimization patterns

## Dependencies
- 07-backend (SQLAlchemy ORM usage via entities/)
- 06-architecture (SQLite/PostgreSQL dual strategy)
- 11-learning-engine (prerequisite graph queries)
- 24-caching (query result caching)

## Sequence: Database Mode Selection
```
Application Start → Read MODE env var → MODE=dev? → SQLite (skillsynth.db)
                                           ↓ No
                                     PostgreSQL (DATABASE_URL)
                                           ↓
                                  Run 003_reduced_schema.sql
                                           ↓
                                  Seed via seed_v3.py
                                           ↓
                                  Auto-create admin if ADMIN_PASSWORD set
```

## State Diagram: Table Lifecycle
```
[Created] → [Seeded] → [Active] → [Soft Deleted] → [Dropped]
                    ↑                              ↓
           [Migrated / Altered]         [Restored / Archived]
```

## ERD References
- docs/40-diagrams/ERD.md for full entity-relationship diagram (15 tables)
- 17+ indexes covering FK lookups, auth, time-range queries

## Table Families
| Family | Tables | Description |
|--------|--------|-------------|
| Identity | users | Authentication, binary admin flag, profile metadata (merged from profiles) |
| Catalog | categories, skills, skill_prerequisites, job_roles, job_role_skills, resources | Skill taxonomy, prerequisite DAG, career roles, resource catalog |
| Assessment | assessments, assessment_questions, assessment_results, user_skills | Skill assessment, normalized question bank, scoring → proficiency |
| Learning | paths, path_steps, step_progress | Learning path generation, step tracking, merged completions+progress |
| Engagement | activity_log | Merged event + audit trail (category ∈ {audit,auth,system,learning,realtime}) |

## Rules
1. seed_v3.py is the single authoritative seed script (replaces seed_v2.py)
2. JSON columns limited to the 4 documented exceptions (assessment_questions.options, path_steps.resource_ids, path_steps.assessment_ids, activity_log.data); all M:N relationships use junction tables
3. FK cascade: CASCADE on ownership FK, SET NULL on optional/soft references
4. Soft delete: deleted_at timestamp on paths; filtered by all queries
5. Index every FK column and every frequently-queried column
6. All queries must be batch-fetch (never N+1 in loop)

## Seed Coverage Policy
- `PYTHONPATH=src python seed_v3.py` populates **all 15 tables** (~1109 rows)
- The seed runs a `PRAGMA foreign_key_check` gate and fails loudly on any FK violation
- Idempotent: runs rebuild the schema from ORM metadata, so the dev DB is always regenerable

## Examples
- Junction pattern: skill_prerequisites (skill_id, prerequisite_id) for the prerequisite DAG
- Seed: `PYTHONPATH=src python seed_v3.py` (~1109 rows, all tables)
- Verify: `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH
- Cascade: deleting a user cascades to paths, step_progress, user_skills, assessment_results, activity_log (SET NULL)

## Edge Cases
- SQLite vs PostgreSQL compatibility (LIKE vs ILIKE, autoincrement syntax)
- Concurrent seed execution with FK constraint ordering
- Recursive category parent_id hierarchy (self-referencing FK)

## Failure Cases
- Database file locked (SQLite) → connection timeout
- PostgreSQL connection refused → no fallback, hard failure
- Migration ordering mismatch → manual SQL execution required

## Recovery Procedures
1. Delete skillsynth.db and re-run `PYTHONPATH=src python seed_v3.py`
2. Check DATABASE_URL format for PostgreSQL
3. Apply migrations manually via SQLite CLI or Supabase SQL editor

## Refactoring Strategy
- Migrate from SQLAlchemy auto-create to explicit Alembic migrations
- Add database connection pooling for production PostgreSQL
- Implement read replicas for analytics queries
