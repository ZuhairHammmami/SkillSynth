# SkillSynth Performance & Data Accuracy Specification

**Date**: 2026-09-02
**Status**: Design approved, pending implementation

## 1. Overview

Two-track refactor of SkillSynth to achieve extreme speed, robustness, and 99.99% data accuracy. Track A (speed) and Track B (DB constraints). Frontend SSR deferred to a future session.

## 2. Track A — Speed

### 2.1 N+1 Query Elimination

**Scope**: Rewrite all serialization loops to use batch-fetch helpers.

**New repository methods** (in `catalog_repository.py`):
- `get_skills_by_map(ids: list[int]) -> dict[int, Skill]` — bulk fetch skills by ID list, return `{id: skill}` dict
- `get_resources_by_map(ids: list[int]) -> dict[int, Resource]` — bulk fetch resources by ID list, return `{id: resource}` dict
- `get_prereqs_by_skill_ids(db: Session, skill_ids: list[int]) -> dict[int, list[Skill]]` — return `{skill_id: [prerequisite Skill, ...]}` for given skill IDs
- `get_categories_map(db: Session) -> dict[int, Category]` — return `{id: Category}` for all categories

**New repository methods** (in `learning_repository.py`):
- `get_user_skills_bulk(user_id: int, skill_ids: list[int]) -> dict[int, UserSkill]` — bulk fetch user_skills for one user, return `{skill_id: user_skill}` dict
- `get_completed_step_ids_bulk(user_id: int, step_ids: list[int]) -> set[int]` — bulk check which steps are completed

**Rewritten service functions**:
- `_serialize_step()` (learning_service.py:243) — accepts pre-fetched maps, does zero queries
- `format_path_detail()` (learning_service.py:307) — pre-fetches all resources/skills/user_skills for the path's steps, passes maps to `_serialize_step()`
- `list_user_paths()` (learning_service.py:394) — pre-fetches across all paths, then serializes
- `progress_dashboard()` (learning_service.py:339) — same pattern, avoids per-path per-step queries
- `_path_progress_list()` (analytics_service.py:24) — remove double-fetch of steps
- `_serialize_skill()` (catalog_service.py:25) — accepts pre-fetched maps
- `_serialize_job_role()` (catalog_service.py:236) — batch-fetch skill links
- `_skill_link()` (catalog_service.py:320) — use skill map instead of individual queries
- `_category_name()` (catalog_service.py:336) — batch-fetch categories, return dict
- `_most_requested_skills()` (admin_service.py:128) — batch-fetch top skills
- `get_all_paths_admin()` (admin_service.py:162) — batch-fetch steps and owners
- `_pick_resource_ids()` (learning_service.py:113) — fetch all resources once per path generation

### 2.2 Index Additions

5 new indexes on hot query paths:

| Table | Columns | Reason |
|-------|---------|--------|
| `activity_log` | `category` | Admin events filtering |
| `activity_log` | `created_at` | Event feed sorting |
| `paths` | `(user_id, status)` | Active paths per user |
| `step_progress` | `(user_id, step_id)` | Completion lookups |
| `assessment_results` | `(user_id, completed_at)` | Results sorting per user |

### 2.3 Pagination

Standardized pagination across 8 list endpoints with `page` and `page_size` query params (defaults: page=1, page_size=50). Response envelope: `{items, total, page, page_size, pages}`.

### 2.4 In-Memory LRU Cache

Using `cachetools.TTLCache` for hot read paths with TTL-based expiry and write-through invalidation. Caches: skill detail (60s), category tree (120s), prerequisite graph (300s), job role skills (120s).

## 3. Track B — Data Accuracy

### 3.1 CHECK Constraints

7 new CHECK constraints on columns with business-meaningful ranges. SQLite CHECK support via table-level constraints in CREATE TABLE.

### 3.2 NOT NULL Cleanup

6 columns get NOT NULL added where business logic requires non-null values.

### 3.3 Seed Validation

Programmatic assertion that `correct < len(options)` for all question bank entries.

### 3.4 Proficiency Range

Move 0..5 clamp into Pydantic schema, remove service/router clamping.

### 3.5 JSON Integrity Optimization

Replace full-table JSON scans in `integrity_repository.py` with SQLite LIKE queries for faster delete guards.

## 4. Verification

- `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH
- `PYTHONPATH=src python -m pytest tests/ -q` → 305+ tests pass
- Manual: profile a 10-step path dashboard load before/after (query count comparison)

## 5. Files Changed (estimated)

~25-30 files across backend services, repositories, routers, DTOs, entities, DDL, seed, and tests.
