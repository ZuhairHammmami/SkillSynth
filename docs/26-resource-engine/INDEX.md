# SS-EDS: Resource Engine

## Purpose
Document how learning resources are stored, selected, and attached to path steps. Resources live in the `resources` table (87 rows seeded by seed_v3.py); there is no separate resource service — selection is a function inside the learning service.

## Responsibilities
- Own the `resources` catalog (title, url, type, language, is_free, is_official, author_or_platform)
- Link resources to skills via `resources.skill_id` (FK → skills, ON DELETE SET NULL)
- Select up to two resources per generated step (`_pick_resource_ids` in src/backend/services/learning_service.py:105)
- Expose admin CRUD for resources (GET/POST/PUT/DELETE under /api/admin/resources)

## Inputs
- Seeded catalog: `PYTHONPATH=src python seed_v3.py` inserts 87 resources
- Learner preferences from the wizard payload (`language`, `format`, `is_free`)
- Skill-to-resource ownership (`resources.skill_id`)

## Outputs
- `path_steps.resource_ids` JSON bridge (documented exception to strict 3NF)
- Resource blocks rendered on step detail (id/title/url/type resolved via GET resources by ids)

## Dependencies
- 10-database (resources table; canonical DDL src/migrations/003_reduced_schema.sql)
- 11-learning-engine (path generation calls the selection helper)
- 09-admin (resource CRUD pages in src/admin-app)

## Current Inventory (dev DB)
```bash
sqlite3 skillsynth.db "SELECT count(*) FROM resources;"          # 87
sqlite3 skillsynth.db "SELECT type, count(*) FROM resources GROUP BY type;"
# documentation 50 · course 15 · interactive 10 · article 7 · book 5
```

## Sequence: Step Resource Selection
```
generate_path → _persist_plan (per planned skill)
  → _pick_resource_ids(db, skill, preferences):
      1. owned = resources where skill_id == skill.id
      2. candidates = pool filtered by is_free preference
      3. filter by format (type) unless "any"
      4. prefer resources matching language, else fall back to full candidates
      5. order owned first, deduplicate, take first 2 ids
  → ids persisted to path_steps.resource_ids
```

## ERD References
- resources: id, title, url, type(50), language(en), is_free, is_official, author_or_platform, skill_id FK
- path_steps.resource_ids → JSON array of resource ids

## Rules
1. Resources are DB rows only — no JSON fallback files exist
2. Maximum 2 resources per step, deduplicated by identity before slicing
3. Free-first honoring is honored only when the wizard preference requests it (default true)
4. Language match is preferred, never mandatory (falls back to unfiltered candidates)
5. Deleting a skill sets resources.skill_id to NULL (ON DELETE SET NULL), never deletes rows
6. Resource URLs are stored as-is; availability is not probed at runtime

## Examples
- Wizard preferences {"is_free": true, "format": "course", "language": "en"} → free courses first, other types as fallback
- Skill with no owned resources → selection draws from the whole filtered pool

## Edge Cases
- Empty pool after filtering → step stores empty resource_ids list
- Same resource relevant to multiple steps → may repeat across steps (deduplication is per-step only)

## Failure Cases
- resources table empty (seed skipped) → all steps render without external links
- Unknown type string in DB → rendered verbatim, no filtering crash

## Recovery Procedures
1. Re-seed: `PYTHONPATH=src python seed_v3.py`
2. Verify counts with the sqlite3 queries above
3. Check /api/admin/resources returns the expected rows (require_admin)

## Refactoring Strategy
- Promote resource_ids JSON to a junction table if per-step resource metadata is ever needed
- Add URL health probing as an offline maintenance job, not a request-time check
