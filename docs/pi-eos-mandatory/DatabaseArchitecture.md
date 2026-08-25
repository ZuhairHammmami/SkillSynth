# Database Architecture

## Schema
- **Size**: 32 active tables + 2 deprecated (removed from code but DB may have artifacts)
- **Normalization**: Strict 3NF — no JSON bridge columns for relationships
- **Cascade Policies**: CASCADE on ownership FK, SET NULL on optional refs
- **Soft Delete**: `deleted_at` timestamp on `users`, `files`

## Table Families
| Family | Tables | Purpose |
|--------|--------|---------|
| Auth | 7 | users, roles, permissions, role_permissions, user_roles, sessions, profiles |
| Skills | 5 | skills, categories, skill_categories, skill_prerequisites, job_roles |
| Content | 5 | resources, resource_sources, resource_tags, resource_progress, assessments |
| Paths | 4 | paths, path_skills, path_steps, step_progress |
| Analytics | 8 | events, notifications, analytics_events, streaks, audit_logs, system_logs, settings, feature_flags |
| Admin | 2 | command_history, files |

## Key Indexes
- Primary keys on all tables (auto-increment integer)
- Foreign key indexes on all relationship columns
- Composite index on `(profile_id, created_at)` for time-series queries
- Index on `deleted_at` for soft-delete filtering

## Database Mode Selection
- Dev: SQLite (`skillsynth.db`), WAL mode, synchronous=NORMAL
- Prod: PostgreSQL via `DATABASE_URL`, pool_size=10

## Migration Strategy
- **Current**: SQLAlchemy `Base.metadata.create_all()` (dev)
- **Target**: Alembic migrations (initialized, stamped at `5215103d04e4`)
- **Seed**: `seed_v2.py` (single authoritative seed script)
