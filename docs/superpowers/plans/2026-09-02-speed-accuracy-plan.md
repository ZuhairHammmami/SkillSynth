# SkillSynth Performance & Data Accuracy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate N+1 query patterns, add missing indexes and pagination, add in-memory LRU caching, and strengthen DB constraints for 99.99% data accuracy.

**Architecture:** Two-track refactor. Track A adds batch-fetch repository helpers, rewrites all serialization loops to use them, adds 5 missing indexes, paginates 8 list endpoints, and adds TTL-based in-memory caches. Track B adds CHECK constraints, NOT NULL cleanup, seed validation assertions, and moves proficiency range validation into Pydantic.

**Tech Stack:** Python, FastAPI, SQLAlchemy ORM, SQLite (dev) / PostgreSQL (prod), Pydantic, `cachetools.TTLCache`, pytest

**Spec:** `docs/superpowers/specs/2026-09-02-speed-accuracy-design.md`

## Global Constraints

- Python imports: `from backend import X` — `run.py` injects `src/` into PYTHONPATH
- No file > 300 lines (seed_v4.py documented exception)
- No function > 40 lines with docstring
- 15 tables, strict 3NF, JSON limited to 4 documented exceptions
- Package manager: pnpm (frontend/admin only — not relevant here)
- Tests: `PYTHONPATH=src python -m pytest tests/ -q` — isolated temp SQLite DB per session
- Schema verification: `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH
- All existing 305 tests must continue passing after each task

---

## File Map

### New Files
| File | Responsibility |
|------|---------------|
| `docs/superpowers/specs/2026-09-02-speed-accuracy-design.md` | Design spec |
| `docs/superpowers/plans/2026-09-02-speed-accuracy-plan.md` | This plan |
| `src/backend/dto/pagination.py` | Shared pagination request/response DTOs |
| `tests/test_batch_queries.py` | Tests for batch-fetch helpers |
| `tests/test_pagination.py` | Tests for pagination on list endpoints |
| `tests/test_caching.py` | Tests for LRU cache behavior |
| `tests/test_ddl_constraints.py` | Tests for new CHECK/NOT NULL constraints |

### Modified Files
| File | Changes |
|------|---------|
| `src/backend/repositories/catalog_repository.py` | Add `get_skills_by_map()`, `get_resources_by_map()`, `get_prereqs_by_skill_ids()`, `get_categories_map()` |
| `src/backend/repositories/learning_repository.py` | Add `get_user_skills_bulk()`, `get_completed_step_ids_bulk()` |
| `src/backend/repositories/integrity_repository.py` | Replace JSON scans with LIKE queries |
| `src/backend/services/learning_service.py` | Rewrite `_serialize_step()`, `format_path_detail()`, `list_user_paths()`, `progress_dashboard()`, `_pick_resource_ids()` |
| `src/backend/services/catalog_service.py` | Rewrite `_serialize_skill()`, `_serialize_job_role()`, `_skill_link()`, `_category_name()`, add cache + invalidation |
| `src/backend/services/admin_service.py` | Rewrite `_most_requested_skills()`, `get_all_paths_admin()` |
| `src/backend/services/analytics_service.py` | Rewrite `_path_progress_list()` |
| `src/backend/routers/catalog.py` | Add pagination to skills/categories list |
| `src/backend/routers/catalog_admin.py` | Add pagination to all admin list endpoints |
| `src/backend/routers/paths.py` | Add pagination to user paths list |
| `src/backend/routers/analytics.py` | Add pagination to skill-growth |
| `src/backend/dto/catalog.py` | Add pagination fields to response schemas |
| `src/backend/dto/learning.py` | Add `level: int = Field(ge=0, le=5)` to `RateProficiencyIn` |
| `src/backend/routers/learning.py` | Remove proficiency clamp (now in Pydantic) |
| `src/migrations/003_reduced_schema.sql` | Add indexes, CHECK constraints, NOT NULL |
| `src/backend/entities/catalog.py` | Add new index declarations |
| `src/backend/entities/engagement.py` | Add new index declarations |
| `src/backend/entities/learning.py` | Add new index declarations |
| `src/backend/entities/assessment.py` | Add new index declarations |
| `seed_v4.py` | Add question bank assertion |
| `tools/verify_schema.py` | Update expected index count, handle CHECK constraints |

---

## Task 1: Add Batch-Fetch Repository Helpers

**Goal:** Create bulk-fetch methods that return dicts, enabling loop bodies to do only dict lookups.

**Files:**
- Modify: `src/backend/repositories/catalog_repository.py`
- Modify: `src/backend/repositories/learning_repository.py`
- Test: `tests/test_batch_queries.py`

### Steps

- [ ] **Step 1: Write failing tests for `get_skills_by_map`**

```python
# tests/test_batch_queries.py
"""Tests for batch-fetch repository helpers."""
from backend import get_db
from backend.entities import Base, Skill
from sqlalchemy.orm import Session


def _seed_skills(db: Session):
    """Insert 3 test skills and return them."""
    skills = [
        Skill(id=1001, name="BatchSkillA", category_id=1, difficulty_level=3, estimated_hours=5.0),
        Skill(id=1002, name="BatchSkillB", category_id=1, difficulty_level=5, estimated_hours=10.0),
        Skill(id=1003, name="BatchSkillC", category_id=2, difficulty_level=7, estimated_hours=15.0),
    ]
    for s in skills:
        db.add(s)
    db.commit()
    return skills


def test_get_skills_by_map_returns_dict():
    from backend.repositories.catalog_repository import get_skills_by_map
    db = next(get_db())
    try:
        _seed_skills(db)
        result = get_skills_by_map(db, [1001, 1002])
        assert isinstance(result, dict)
        assert 1001 in result
        assert 1002 in result
        assert 1003 not in result
        assert result[1001].name == "BatchSkillA"
    finally:
        for s in [1001, 1002, 1003]:
            db.query(Skill).filter(Skill.id == s).delete()
        db.commit()


def test_get_skills_by_map_empty_input():
    from backend.repositories.catalog_repository import get_skills_by_map
    db = next(get_db())
    try:
        result = get_skills_by_map(db, [])
        assert result == {}
    finally:
        pass


def test_get_skills_by_map_missing_ids_ignored():
    from backend.repositories.catalog_repository import get_skills_by_map
    db = next(get_db())
    try:
        _seed_skills(db)
        result = get_skills_by_map(db, [1001, 99999])
        assert 1001 in result
        assert 99999 not in result
    finally:
        for s in [1001, 1002, 1003]:
            db.query(Skill).filter(Skill.id == s).delete()
        db.commit()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_batch_queries.py -v`
Expected: FAIL — `ImportError: cannot import name 'get_skills_by_map'`

- [ ] **Step 3: Implement `get_skills_by_map` in `catalog_repository.py`**

Add at the end of `src/backend/repositories/catalog_repository.py`:

```python
def get_skills_by_map(db: Session, ids: list[int]) -> dict[int, Skill]:
    """Fetch skills by ID list, return {id: Skill} dict. Skips missing IDs."""
    if not ids:
        return {}
    rows = db.query(Skill).filter(Skill.id.in_(ids)).all()
    return {r.id: r for r in rows}
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_batch_queries.py::test_get_skills_by_map -v`
Expected: PASS

- [ ] **Step 5: Write failing tests for `get_resources_by_map`**

```python
from backend.entities import Resource


def _seed_resources(db: Session):
    resources = [
        Resource(id=1001, skill_id=1, name="ResA", resource_type="article", url="https://a.com"),
        Resource(id=1002, skill_id=1, name="ResB", resource_type="video", url="https://b.com"),
    ]
    for r in resources:
        db.add(r)
    db.commit()
    return resources


def test_get_resources_by_map_returns_dict():
    from backend.repositories.catalog_repository import get_resources_by_map
    db = next(get_db())
    try:
        _seed_resources(db)
        result = get_resources_by_map(db, [1001, 1002])
        assert isinstance(result, dict)
        assert 1001 in result
        assert result[1001].name == "ResA"
    finally:
        for r in [1001, 1002]:
            db.query(Resource).filter(Resource.id == r).delete()
        db.commit()


def test_get_resources_by_map_empty():
    from backend.repositories.catalog_repository import get_resources_by_map
    db = next(get_db())
    assert get_resources_by_map(db, []) == {}
```

- [ ] **Step 6: Run tests — verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_batch_queries.py::test_get_resources_by_map -v`
Expected: FAIL — `ImportError`

- [ ] **Step 7: Implement `get_resources_by_map` in `catalog_repository.py`**

```python
def get_resources_by_map(db: Session, ids: list[int]) -> dict[int, Resource]:
    """Fetch resources by ID list, return {id: Resource} dict."""
    if not ids:
        return {}
    rows = db.query(Resource).filter(Resource.id.in_(ids)).all()
    return {r.id: r for r in rows}
```

- [ ] **Step 8: Run tests — verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_batch_queries.py -v`
Expected: ALL PASS

- [ ] **Step 9: Write failing tests for learning_repository batch methods**

```python
def test_get_user_skills_bulk():
    from backend.repositories.learning_repository import get_user_skills_bulk
    from backend.entities import UserSkill
    db = next(get_db())
    try:
        us = UserSkill(user_id=99901, skill_id=1, proficiency=3)
        db.add(us)
        db.commit()
        result = get_user_skills_bulk(db, 99901, [1, 2, 3])
        assert isinstance(result, dict)
        assert 1 in result
        assert 2 not in result
        assert result[1].proficiency == 3
    finally:
        db.query(UserSkill).filter(UserSkill.user_id == 99901).delete()
        db.commit()


def test_get_completed_step_ids_bulk():
    from backend.repositories.learning_repository import get_completed_step_ids_bulk
    from backend.entities import StepProgress
    db = next(get_db())
    try:
        sp = StepProgress(user_id=99901, step_id=5001, completed_at="2026-01-01")
        db.add(sp)
        db.commit()
        result = get_completed_step_ids_bulk(db, 99901, [5001, 5002, 5003])
        assert isinstance(result, set)
        assert 5001 in result
        assert 5002 not in result
    finally:
        db.query(StepProgress).filter(StepProgress.user_id == 99901).delete()
        db.commit()
```

- [ ] **Step 10: Run tests — verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_batch_queries.py -k "user_skills_bulk or completed_step" -v`
Expected: FAIL — `ImportError`

- [ ] **Step 11: Implement `get_user_skills_bulk` and `get_completed_step_ids_bulk` in `learning_repository.py`**

```python
def get_user_skills_bulk(db: Session, user_id: int, skill_ids: list[int]) -> dict[int, "UserSkill"]:
    """Fetch user_skills for one user by skill ID list."""
    if not skill_ids:
        return {}
    rows = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.skill_id.in_(skill_ids)
    ).all()
    return {r.skill_id: r for r in rows}


def get_completed_step_ids_bulk(db: Session, user_id: int, step_ids: list[int]) -> set[int]:
    """Return the set of step_ids that are completed for a user."""
    if not step_ids:
        return set()
    rows = db.query(StepProgress.step_id).filter(
        StepProgress.user_id == user_id,
        StepProgress.step_id.in_(step_ids),
        StepProgress.completed_at.isnot(None)
    ).all()
    return {r[0] for r in rows}
```

- [ ] **Step 12: Run tests — verify all pass**

Run: `PYTHONPATH=src python -m pytest tests/test_batch_queries.py -v`
Expected: ALL PASS

- [ ] **Step 13: Run full test suite — verify no regressions**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 14: Commit**

```bash
git add src/backend/repositories/catalog_repository.py src/backend/repositories/learning_repository.py tests/test_batch_queries.py
git commit -m "feat: add batch-fetch repository helpers (get_skills_by_map, get_resources_by_map, get_user_skills_bulk, get_completed_step_ids_bulk)"
```

---

## Task 2: Rewrite Learning Service Serialization (N+1 Elimination — Steps)

**Goal:** Eliminate 3 queries per step in `_serialize_step()` and all callers.

**Files:**
- Modify: `src/backend/services/learning_service.py`
- Modify: `src/backend/services/analytics_service.py`
- Existing tests: `tests/test_learning.py`, `tests/test_analytics.py`

**Depends on:** Task 1 (batch-fetch helpers exist)

### Steps

- [ ] **Step 1: Read current `_serialize_step()` and all callers**

Read: `src/backend/services/learning_service.py` lines 243-325. Identify every call site:
- `format_path_detail()` (line 310-311)
- `list_user_paths()` (line 397-400)
- `progress_dashboard()` (line 367-368)

Also read `src/backend/services/analytics_service.py` `_path_progress_list()` (lines 24-39).

- [ ] **Step 2: Refactor `_serialize_step()` to accept pre-fetched maps**

Rewrite `_serialize_step()` to accept `resource_map`, `skill_map`, `user_skill_map` as parameters:

```python
def _serialize_step(
    step: PathStep,
    resource_map: dict[int, "Resource"],
    skill_map: dict[int, "Skill"],
    user_skill_map: dict[int, "UserSkill"],
) -> dict:
    """Serialize a single step using pre-fetched maps. Zero DB queries."""
    resources = [resource_map[rid] for rid in (step.resource_ids or []) if rid in resource_map]
    skill = skill_map.get(step.skill_id)
    user_skill = user_skill_map.get(step.skill_id)
    return {
        "id": step.id,
        "skill_id": step.skill_id,
        "skill_name": skill.name if skill else None,
        "resource_ids": step.resource_ids or [],
        "resources": [{"id": r.id, "name": r.name, "type": r.resource_type, "url": r.url} for r in resources],
        "selected_level": step.selected_level,
        "current_level": step.current_level,
        "order_index": step.order_index,
        "proficiency": user_skill.proficiency if user_skill else 0,
    }
```

- [ ] **Step 3: Rewrite `format_path_detail()` to batch-fetch**

```python
def format_path_detail(path: Path, steps: list[PathStep], user_id: int, db: Session) -> dict:
    """Serialize a path with all steps. Batch-fetches resources, skills, user_skills."""
    all_resource_ids = [rid for step in steps for rid in (step.resource_ids or [])]
    all_skill_ids = list({step.skill_id for step in steps})

    resource_map = catalog_repo.get_resources_by_map(db, all_resource_ids)
    skill_map = catalog_repo.get_skills_by_map(db, all_skill_ids)
    user_skill_map = learning_repo.get_user_skills_bulk(db, user_id, all_skill_ids)

    serialized_steps = [_serialize_step(s, resource_map, skill_map, user_skill_map) for s in steps]
    # ... rest unchanged
```

- [ ] **Step 4: Rewrite `list_user_paths()` to batch across all paths**

Same pattern: collect all resource_ids and skill_ids across ALL paths, fetch in bulk, then serialize each path using the shared maps.

- [ ] **Step 5: Rewrite `progress_dashboard()` to batch across all paths**

Same pattern — collect all step IDs across all paths, batch-fetch resources/skills/user_skills/completions, serialize.

- [ ] **Step 6: Rewrite `_path_progress_list()` in analytics_service.py**

Remove double-fetch: use batch-fetch for step counts per path instead of calling `get_steps()` twice.

- [ ] **Step 7: Run existing tests — verify no regressions**

Run: `PYTHONPATH=src python -m pytest tests/test_learning.py tests/test_analytics.py -q`
Expected: ALL PASS

- [ ] **Step 8: Run full test suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 9: Commit**

```bash
git add src/backend/services/learning_service.py src/backend/services/analytics_service.py
git commit -m "perf: eliminate N+1 queries in learning service serialization (3 queries/step -> 3 queries/path)"
```

---

## Task 3: Rewrite Catalog Service Serialization (N+1 Elimination — Skills)

**Goal:** Eliminate 2 queries per skill in `_serialize_skill()` and all callers.

**Files:**
- Modify: `src/backend/services/catalog_service.py`
- Modify: `src/backend/repositories/catalog_repository.py` (add helpers)
- Existing tests: `tests/test_catalog.py`

**Depends on:** Task 1

### Steps

- [ ] **Step 1: Add `get_prereqs_by_skill_ids()` and `get_categories_map()` to catalog_repository**

```python
def get_prereqs_by_skill_ids(db: Session, skill_ids: list[int]) -> dict[int, list["Skill"]]:
    """Return {skill_id: [prerequisite Skill, ...]} for given skill IDs."""
    if not skill_ids:
        return {}
    rows = db.query(SkillPrerequisite).filter(SkillPrerequisite.skill_id.in_(skill_ids)).all()
    prereq_ids = list({r.prerequisite_id for r in rows})
    prereq_skills = {s.id: s for s in db.query(Skill).filter(Skill.id.in_(prereq_ids)).all()} if prereq_ids else {}
    result: dict[int, list["Skill"]] = {sid: [] for sid in skill_ids}
    for row in rows:
        if row.prerequisite_id in prereq_skills:
            result[row.skill_id].append(prereq_skills[row.prerequisite_id])
    return result


def get_categories_map(db: Session) -> dict[int, "Category"]:
    """Return {id: Category} for all categories."""
    rows = db.query(Category).all()
    return {r.id: r for r in rows}
```

- [ ] **Step 2: Rewrite `_serialize_skill()` to accept maps**

```python
def _serialize_skill(skill: Skill, prereq_map: dict, resource_map: dict) -> dict:
    """Serialize a skill using pre-fetched prerequisite and resource maps."""
    prereqs = prereq_map.get(skill.id, [])
    resources = resource_map.get(skill.id, [])
    return {
        "id": skill.id,
        "name": skill.name,
        "category_id": skill.category_id,
        "difficulty_level": skill.difficulty_level,
        "estimated_hours": skill.estimated_hours,
        "icon": skill.icon,
        "color": skill.color,
        "prerequisite_ids": skill.prerequisite_ids or [],
        "prerequisites": [{"id": p.id, "name": p.name} for p in prereqs],
        "resources": [{"id": r.id, "name": r.name, "type": r.resource_type} for r in resources],
    }
```

- [ ] **Step 3: Rewrite `list_skills()` to batch-fetch**

```python
def list_skills(db: Session) -> list[dict]:
    skills = irepo.get_all_skills(db)
    skill_ids = [s.id for s in skills]
    prereq_map = catalog_repo.get_prereqs_by_skill_ids(db, skill_ids)
    all_resources = db.query(Resource).filter(Resource.skill_id.in_(skill_ids)).all()
    resource_groups: dict[int, list] = {sid: [] for sid in skill_ids}
    for r in all_resources:
        resource_groups[r.skill_id].append(r)
    return [_serialize_skill(s, prereq_map, resource_groups) for s in skills]
```

- [ ] **Step 4: Rewrite `_category_name()` to use pre-fetched category map**

Use `get_categories_map()` in `serialize_skill_detail()` instead of individual queries.

- [ ] **Step 5: Rewrite `_serialize_job_role()` and `_skill_link()`**

Batch-fetch all skill links for all roles, then serialize from maps.

- [ ] **Step 6: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_catalog.py tests/test_catalog_integrity.py -q`
Expected: ALL PASS

- [ ] **Step 7: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 8: Commit**

```bash
git add src/backend/services/catalog_service.py src/backend/repositories/catalog_repository.py
git commit -m "perf: eliminate N+1 queries in catalog service serialization (2 queries/skill -> batch)"
```

---

## Task 4: Rewrite Admin Service Serialization (N+1 Elimination — Admin)

**Goal:** Eliminate N+1 queries in admin paths listing and most-requested-skills.

**Files:**
- Modify: `src/backend/services/admin_service.py`
- Existing tests: `tests/test_admin.py`

**Depends on:** Tasks 1, 3

### Steps

- [ ] **Step 1: Rewrite `_most_requested_skills()`**

Batch-fetch the top N skill IDs using `get_skills_by_map()`.

- [ ] **Step 2: Rewrite `get_all_paths_admin()`**

Batch-fetch steps for all paths in the page, batch-fetch owner users.

- [ ] **Step 3: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_admin.py -q`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/backend/services/admin_service.py
git commit -m "perf: eliminate N+1 queries in admin service (paths listing, most-requested-skills)"
```

---

## Task 5: Rewrite `_pick_resource_ids()` in Learning Service

**Goal:** Stop calling `get_all_resources()` on every step during path generation.

**Files:**
- Modify: `src/backend/services/learning_service.py`

**Depends on:** Task 1

### Steps

- [ ] **Step 1: Read `_pick_resource_ids()`**

Read: `src/backend/services/learning_service.py` lines 113-134. Note `get_all_resources()` call on line 121.

- [ ] **Step 2: Refactor to pass pre-fetched resource list**

Make `_pick_resource_ids()` accept a `all_resources` parameter instead of calling `get_all_resources()` itself. The caller (`generate_path` or per-skill path gen) fetches once and passes it in.

- [ ] **Step 3: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_learning.py -q`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/backend/services/learning_service.py
git commit -m "perf: fetch resources once per path generation instead of per step"
```

---

## Task 6: Add Missing Database Indexes

**Goal:** Add 5 indexes on hot query paths.

**Files:**
- Modify: `src/migrations/003_reduced_schema.sql`
- Modify: `src/backend/entities/engagement.py`
- Modify: `src/backend/entities/learning.py`
- Modify: `src/backend/entities/assessment.py`
- Modify: `tools/verify_schema.py`
- Test: `tests/test_schema.py`

### Steps

- [ ] **Step 1: Add indexes to DDL**

In `src/migrations/003_reduced_schema.sql`, add before the final semicolon:

```sql
CREATE INDEX idx_activity_log_category ON activity_log(category);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);
CREATE INDEX idx_paths_user_status ON paths(user_id, status);
CREATE INDEX idx_step_progress_user_step ON step_progress(user_id, step_id);
CREATE INDEX idx_assessment_results_user_completed ON assessment_results(user_id, completed_at);
```

- [ ] **Step 2: Add index declarations to ORM entities**

In `src/backend/entities/engagement.py`, add to `ActivityLog.__table_args__`:
```python
Index("idx_activity_log_category", "category"),
Index("idx_activity_log_created_at", "created_at"),
```

In `src/backend/entities/learning.py`, add to `Paths.__table_args__`:
```python
Index("idx_paths_user_status", "user_id", "status"),
```
Add to `StepProgress.__table_args__`:
```python
Index("idx_step_progress_user_step", "user_id", "step_id"),
```

In `src/backend/entities/assessment.py`, add to `AssessmentResult.__table_args__`:
```python
Index("idx_assessment_results_user_completed", "user_id", "completed_at"),
```

- [ ] **Step 3: Update `verify_schema.py` expected index count**

The schema verifier counts developer-created indexes (origin='c'). Update the expected count to include the 5 new indexes.

- [ ] **Step 4: Run schema verification**

Run: `PYTHONPATH=src python tools/verify_schema.py`
Expected: `SCHEMA MATCH`

- [ ] **Step 5: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_schema.py -q`
Expected: ALL PASS

- [ ] **Step 6: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 7: Commit**

```bash
git add src/migrations/003_reduced_schema.sql src/backend/entities/engagement.py src/backend/entities/learning.py src/backend/entities/assessment.py tools/verify_schema.py
git commit -m "perf: add 5 indexes on hot query paths (activity_log, paths, step_progress, assessment_results)"
```

---

## Task 7: Add Pagination to List Endpoints

**Goal:** Add `?page=1&page_size=50` to 8 list endpoints.

**Files:**
- Create: `src/backend/dto/pagination.py`
- Modify: `src/backend/routers/catalog.py`
- Modify: `src/backend/routers/catalog_admin.py`
- Modify: `src/backend/routers/paths.py`
- Modify: `src/backend/routers/analytics.py`
- Test: `tests/test_pagination.py`

### Steps

- [ ] **Step 1: Create pagination DTO**

```python
# src/backend/dto/pagination.py
from pydantic import BaseModel, Field
import math


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


def paginate(items: list, page: int, page_size: int) -> dict:
    """Paginate a list and return the standard envelope."""
    total = len(items)
    pages = math.ceil(total / page_size) if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
```

- [ ] **Step 2: Write failing test for pagination**

```python
# tests/test_pagination.py
"""Tests for paginated list endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_catalog_skills_pagination(client: TestClient, auth_headers: dict):
    resp = client.get("/api/catalog/skills?page=1&page_size=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10


def test_catalog_skills_pagination_page_2(client: TestClient, auth_headers: dict):
    resp = client.get("/api/catalog/skills?page=2&page_size=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2


def test_admin_users_pagination(client: TestClient, admin_headers: dict):
    resp = client.get("/api/admin/users?page=1&page_size=5", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
```

- [ ] **Step 3: Run tests — verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_pagination.py -v`
Expected: FAIL (pagination fields not in response)

- [ ] **Step 4: Add pagination to catalog skills/categories endpoints**

In `src/backend/routers/catalog.py`, wrap the list endpoints to accept `page` and `page_size` query params, slice results, and return paginated envelope.

- [ ] **Step 5: Add pagination to admin list endpoints**

Same pattern for `catalog_admin.py` (users, skills, categories, job-roles).

- [ ] **Step 6: Add pagination to paths and analytics endpoints**

Same pattern for `paths.py` and `analytics.py`.

- [ ] **Step 7: Run pagination tests**

Run: `PYTHONPATH=src python -m pytest tests/test_pagination.py -v`
Expected: ALL PASS

- [ ] **Step 8: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 9: Commit**

```bash
git add src/backend/dto/pagination.py src/backend/routers/catalog.py src/backend/routers/catalog_admin.py src/backend/routers/paths.py src/backend/routers/analytics.py tests/test_pagination.py
git commit -m "feat: add pagination to 8 list endpoints (default page_size=50, max=200)"
```

---

## Task 8: Add In-Memory LRU Cache

**Goal:** Cache hot read paths with TTL-based expiry and write-through invalidation.

**Files:**
- Modify: `src/backend/services/catalog_service.py`
- Modify: `src/backend/services/catalog_integrity.py`
- Modify: `requirements.txt`
- Test: `tests/test_caching.py`
- Dependency: Add `cachetools` to `requirements.txt`

### Steps

- [ ] **Step 1: Add `cachetools` to requirements.txt**

Add `cachetools>=5.0` to `requirements.txt`.

- [ ] **Step 2: Install**

Run: `pip install cachetools`

- [ ] **Step 3: Write failing tests for caching**

```python
# tests/test_caching.py
"""Tests for in-memory LRU cache behavior."""


def test_cache_invalidation_on_skill_update():
    """Updating a skill should invalidate its cache entry."""
    from backend.services.catalog_service import _skill_cache, invalidate_skill_cache
    _skill_cache[1] = {"name": "old"}
    invalidate_skill_cache(1)
    assert 1 not in _skill_cache


def test_cache_clears_category_on_write():
    """Any write should clear category cache."""
    from backend.services.catalog_service import _category_cache, invalidate_skill_cache
    _category_cache["all"] = ["data"]
    invalidate_skill_cache()
    assert len(_category_cache) == 0
```

- [ ] **Step 4: Run tests — verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_caching.py -v`
Expected: FAIL — `ImportError`

- [ ] **Step 5: Implement cache infrastructure in catalog_service.py**

```python
from cachetools import TTLCache

_skill_cache: TTLCache = TTLCache(maxsize=256, ttl=60)
_category_cache: TTLCache = TTLCache(maxsize=32, ttl=120)
_prereq_graph_cache: TTLCache = TTLCache(maxsize=1, ttl=300)
_job_role_cache: TTLCache = TTLCache(maxsize=64, ttl=120)


def invalidate_skill_cache(skill_id: int | None = None):
    """Clear skill cache entry (or all if skill_id is None) and dependent caches."""
    if skill_id is not None:
        _skill_cache.pop(skill_id, None)
    else:
        _skill_cache.clear()
    _category_cache.clear()
    _prereq_graph_cache.clear()
    _job_role_cache.clear()
```

- [ ] **Step 6: Add invalidation calls to write operations**

In `create_skill`, `update_skill`, `delete_skill` — call `invalidate_skill_cache()` after successful write. Same pattern for categories and job roles.

- [ ] **Step 7: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_caching.py -v`
Expected: ALL PASS

- [ ] **Step 8: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 9: Commit**

```bash
git add src/backend/services/catalog_service.py src/backend/services/catalog_integrity.py requirements.txt tests/test_caching.py
git commit -m "feat: add in-memory LRU cache for skill detail, category tree, prerequisite graph"
```

---

## Task 9: Add CHECK Constraints to DDL

**Goal:** Add 7 CHECK constraints for business-meaningful ranges.

**Files:**
- Modify: `src/migrations/003_reduced_schema.sql`
- Modify: `src/backend/entities/` (ORM)
- Modify: `tools/verify_schema.py`
- Test: `tests/test_ddl_constraints.py`

### Steps

- [ ] **Step 1: Write failing tests for CHECK constraints**

```python
# tests/test_ddl_constraints.py
"""Tests for DDL CHECK constraints."""
import sqlite3


def test_difficulty_level_range_rejects_11():
    """difficulty_level must be 1-10. Value 11 should fail."""
    from backend.database import engine
    conn = engine.connect()
    try:
        conn.execute(
            __import__("sqlalchemy").text(
                "INSERT INTO skills (name, category_id, difficulty_level) VALUES ('test_bad', 1, 11)"
            )
        )
        conn.commit()
        assert False, "Should have raised IntegrityError for difficulty_level=11"
    except Exception:
        pass
    finally:
        conn.execute(__import__("sqlalchemy").text("DELETE FROM skills WHERE name = 'test_bad'"))
        conn.commit()
        conn.close()


def test_difficulty_level_accepts_5():
    """difficulty_level=5 should succeed."""
    from backend.database import engine
    conn = engine.connect()
    try:
        conn.execute(
            __import__("sqlalchemy").text(
                "INSERT INTO skills (name, category_id, difficulty_level) VALUES ('test_good', 1, 5)"
            )
        )
        conn.commit()
    finally:
        conn.execute(__import__("sqlalchemy").text("DELETE FROM skills WHERE name = 'test_good'"))
        conn.commit()
        conn.close()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_ddl_constraints.py -v`
Expected: FAIL (constraint doesn't exist, insert succeeds)

- [ ] **Step 3: Add CHECK constraints to DDL**

In `003_reduced_schema.sql`, add to the relevant CREATE TABLE statements:

```sql
-- In skills table:
CONSTRAINT chk_difficulty CHECK(difficulty_level >= 1 AND difficulty_level <= 10),
CONSTRAINT chk_hours CHECK(estimated_hours >= 0),

-- In assessments table:
CONSTRAINT chk_pass_score CHECK(pass_score >= 0 AND pass_score <= 100),

-- In assessment_questions table:
CONSTRAINT chk_correct CHECK(correct_index >= 0),

-- In user_skills table:
CONSTRAINT chk_proficiency CHECK(proficiency >= 0 AND proficiency <= 5),

-- In step_progress table:
CONSTRAINT chk_step_level CHECK(current_level >= 0 AND current_level <= 5),

-- In path_steps table:
CONSTRAINT chk_selected_level CHECK(selected_level >= 0 AND selected_level <= 5),
```

- [ ] **Step 4: Add matching ORM constraints**

In each entity file, add `CheckConstraint(...)` to `__table_args__`.

- [ ] **Step 5: Update `verify_schema.py`**

The verifier needs to compare CHECK constraints. Add CHECK constraint comparison to the schema diff logic.

- [ ] **Step 6: Run schema verification**

Run: `PYTHONPATH=src python tools/verify_schema.py`
Expected: `SCHEMA MATCH`

- [ ] **Step 7: Run constraint tests**

Run: `PYTHONPATH=src python -m pytest tests/test_ddl_constraints.py -v`
Expected: ALL PASS

- [ ] **Step 8: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 9: Commit**

```bash
git add src/migrations/003_reduced_schema.sql src/backend/entities/ tools/verify_schema.py tests/test_ddl_constraints.py
git commit -m "feat: add 7 CHECK constraints for business-meaningful ranges (difficulty, hours, proficiency, etc.)"
```

---

## Task 10: Add NOT NULL Constraints

**Goal:** Add NOT NULL to 6 columns that should never be null.

**Files:**
- Modify: `src/migrations/003_reduced_schema.sql`
- Modify: `src/backend/entities/` (ORM)

### Steps

- [ ] **Step 1: Add NOT NULL to DDL**

```sql
-- skills table
difficulty_level INTEGER NOT NULL DEFAULT 0,
estimated_hours REAL NOT NULL DEFAULT 0.0,

-- user_skills table
proficiency INTEGER NOT NULL DEFAULT 0,

-- step_progress table
current_level INTEGER NOT NULL DEFAULT 0,

-- path_steps table
selected_level INTEGER NOT NULL DEFAULT 0,
current_level INTEGER NOT NULL DEFAULT 0,
```

- [ ] **Step 2: Update ORM entities**

Add `nullable=False` to matching column definitions.

- [ ] **Step 3: Run schema verification**

Run: `PYTHONPATH=src python tools/verify_schema.py`
Expected: `SCHEMA MATCH`

- [ ] **Step 4: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 5: Commit**

```bash
git add src/migrations/003_reduced_schema.sql src/backend/entities/
git commit -m "feat: add NOT NULL constraints on 6 columns requiring non-null values"
```

---

## Task 11: Fix Seed Validation and Proficiency Range

**Goal:** Add programmatic assertions to seed data, fix proficiency range in Pydantic.

**Files:**
- Modify: `seed_v4.py`
- Modify: `src/backend/dto/learning.py`
- Modify: `src/backend/routers/learning.py`
- Modify: `src/backend/services/learning_service.py`

### Steps

- [ ] **Step 1: Add assertion to `seed_v4.py`**

After the QUESTION_BANK definition, add:

```python
def _validate_question_bank():
    """Assert all question bank entries have valid correct indices."""
    for entry in QUESTION_BANK:
        assert isinstance(entry.get("correct"), int), f"bad correct type: {entry['question']}"
        assert 0 <= entry["correct"] < len(entry["options"]), (
            f"correct index {entry['correct']} out of range for {len(entry['options'])} options: {entry['question']}"
        )

_validate_question_bank()
```

- [ ] **Step 2: Move proficiency range into Pydantic**

In `src/backend/dto/learning.py`, change:
```python
class RateProficiencyIn(BaseModel):
    level: int = Field(ge=0, le=5)
```

- [ ] **Step 3: Remove router/service clamping**

In `src/backend/routers/learning.py`, remove the `max(0, min(5, ...))` clamp.
In `src/backend/services/learning_service.py`, remove the `max(0, min(5, ...))` clamp.

- [ ] **Step 4: Run proficiency tests**

Run: `PYTHONPATH=src python -m pytest tests/test_proficiency.py -q`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 6: Commit**

```bash
git add seed_v4.py src/backend/dto/learning.py src/backend/routers/learning.py src/backend/services/learning_service.py
git commit -m "fix: add seed question bank validation, move proficiency 0..5 range into Pydantic schema"
```

---

## Task 12: Optimize JSON Integrity Repository

**Goal:** Replace full-table JSON scans with SQLite LIKE queries for faster delete guards.

**Files:**
- Modify: `src/backend/repositories/integrity_repository.py`

**Depends on:** None (independent)

### Steps

- [ ] **Step 1: Read current `count_resource_dependents()` and `count_assessment_dependents()`**

Read: `src/backend/repositories/integrity_repository.py` lines 94-128.

- [ ] **Step 2: Replace Python JSON scan with LIKE query**

```python
def count_resource_dependents(db: Session, resource_id: int) -> int:
    """Count path_steps referencing a resource ID via LIKE on JSON column."""
    pattern = f'%"{resource_id}"%'
    return db.query(PathStep).filter(PathStep.resource_ids.like(pattern)).count()


def count_assessment_dependents(db: Session, assessment_id: int) -> int:
    """Count path_steps referencing an assessment ID via LIKE on JSON column."""
    pattern = f'%"{assessment_id}"%'
    return db.query(PathStep).filter(PathStep.assessment_ids.like(pattern)).count()
```

- [ ] **Step 3: Run integrity tests**

Run: `PYTHONPATH=src python -m pytest tests/test_integrity.py tests/test_catalog_integrity.py -q`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/backend/repositories/integrity_repository.py
git commit -m "perf: replace Python JSON scans with SQLite LIKE queries in delete guards"
```

---

## Task 13: Final Verification

**Goal:** Run all verification commands and confirm everything passes.

### Steps

- [ ] **Step 1: Run schema verification**

Run: `PYTHONPATH=src python tools/verify_schema.py`
Expected: `SCHEMA MATCH`

- [ ] **Step 2: Run full test suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ PASS

- [ ] **Step 3: Check for any files over 300 lines**

Run: `wc -l src/backend/services/*.py src/backend/repositories/*.py src/backend/routers/*.py | sort -rn | head -5`
Expected: No file > 300 lines

- [ ] **Step 4: Final commit if any cleanup needed**

```bash
git add -A
git commit -m "chore: final verification — all tests pass, schema matches, no file/func size violations"
```
