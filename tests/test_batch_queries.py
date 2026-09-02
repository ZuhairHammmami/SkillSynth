"""Tests for batch-fetch repository helpers (N+1 elimination layer)."""

import pytest
from backend.entities.catalog import Category, Resource, Skill, SkillPrerequisite
from backend.entities.learning import StepProgress, UserSkill


# ── Seed helpers ──

_TEST_SKILL_IDS = [1001, 1002, 1003]
_TEST_RESOURCE_IDS = [1001, 1002]
_TEST_CAT_IDS = [8001, 8002]


def _seed_skills(db):
    """Insert 3 test skills with high IDs to avoid seed collisions."""
    skills = [
        Skill(id=1001, name="BatchSkillA", category_id=1,
              difficulty_level=3, estimated_hours=5),
        Skill(id=1002, name="BatchSkillB", category_id=1,
              difficulty_level=5, estimated_hours=10),
        Skill(id=1003, name="BatchSkillC", category_id=2,
              difficulty_level=7, estimated_hours=15),
    ]
    for s in skills:
        db.add(s)
    db.commit()


def _seed_resources(db):
    """Insert 2 test resources."""
    resources = [
        Resource(id=1001, skill_id=1, title="ResA", type="article",
                 url="https://a.com"),
        Resource(id=1002, skill_id=1, title="ResB", type="video",
                 url="https://b.com"),
    ]
    for r in resources:
        db.add(r)
    db.commit()


def _seed_prereqs(db):
    """Insert 3 skills + prerequisite edges."""
    _seed_skills(db)
    edges = [
        SkillPrerequisite(skill_id=1002, prerequisite_id=1001),
        SkillPrerequisite(skill_id=1003, prerequisite_id=1001),
        SkillPrerequisite(skill_id=1003, prerequisite_id=1002),
    ]
    for e in edges:
        db.add(e)
    db.commit()


def _seed_categories(db):
    """Insert 2 test categories."""
    cats = [
        Category(id=8001, name="BatchCatA"),
        Category(id=8002, name="BatchCatB"),
    ]
    for c in cats:
        db.add(c)
    db.commit()


def _cleanup(db, model, ids, id_col="id"):
    """Delete rows by primary key list for a given model."""
    col = getattr(model, id_col)
    for rid in ids:
        db.query(model).filter(col == rid).delete()
    db.commit()


# ── get_skills_by_map ──


def test_get_skills_by_map_returns_dict(db_session):
    from backend.repositories.catalog_repository import get_skills_by_map
    _seed_skills(db_session)
    try:
        result = get_skills_by_map(db_session, [1001, 1002])
        assert isinstance(result, dict)
        assert 1001 in result
        assert 1002 in result
        assert 1003 not in result
        assert result[1001].name == "BatchSkillA"
    finally:
        _cleanup(db_session, Skill, _TEST_SKILL_IDS)


def test_get_skills_by_map_empty(db_session):
    from backend.repositories.catalog_repository import get_skills_by_map
    assert get_skills_by_map(db_session, []) == {}


def test_get_skills_by_map_missing_ignored(db_session):
    from backend.repositories.catalog_repository import get_skills_by_map
    _seed_skills(db_session)
    try:
        result = get_skills_by_map(db_session, [1001, 99999])
        assert 1001 in result
        assert 99999 not in result
    finally:
        _cleanup(db_session, Skill, _TEST_SKILL_IDS)


# ── get_resources_by_map ──


def test_get_resources_by_map_returns_dict(db_session):
    from backend.repositories.catalog_repository import get_resources_by_map
    _seed_resources(db_session)
    try:
        result = get_resources_by_map(db_session, [1001, 1002])
        assert isinstance(result, dict)
        assert 1001 in result
        assert result[1001].title == "ResA"
    finally:
        _cleanup(db_session, Resource, _TEST_RESOURCE_IDS)


def test_get_resources_by_map_empty(db_session):
    from backend.repositories.catalog_repository import get_resources_by_map
    assert get_resources_by_map(db_session, []) == {}


# ── get_prereqs_by_skill_ids ──


def test_get_prereqs_by_skill_ids_groups(db_session):
    from backend.repositories.catalog_repository import get_prereqs_by_skill_ids
    _seed_prereqs(db_session)
    try:
        result = get_prereqs_by_skill_ids(db_session, [1002, 1003])
        assert isinstance(result, dict)
        assert 1002 in result
        assert 1003 in result
        prereq_ids_2 = {s.id for s in result[1002]}
        prereq_ids_3 = {s.id for s in result[1003]}
        assert prereq_ids_2 == {1001}
        assert prereq_ids_3 == {1001, 1002}
    finally:
        db_session.query(SkillPrerequisite).filter(
            SkillPrerequisite.skill_id.in_([1001, 1002, 1003])
        ).delete(synchronize_session=False)
        _cleanup(db_session, Skill, _TEST_SKILL_IDS)


def test_get_prereqs_by_skill_ids_empty(db_session):
    from backend.repositories.catalog_repository import get_prereqs_by_skill_ids
    assert get_prereqs_by_skill_ids(db_session, []) == {}


def test_get_prereqs_by_skill_ids_no_prereqs(db_session):
    from backend.repositories.catalog_repository import get_prereqs_by_skill_ids
    _seed_skills(db_session)
    try:
        result = get_prereqs_by_skill_ids(db_session, [1001])
        assert result == {1001: []}
    finally:
        _cleanup(db_session, Skill, _TEST_SKILL_IDS)


# ── get_categories_map ──


def test_get_categories_map_returns_all(db_session):
    from backend.repositories.catalog_repository import get_categories_map
    _seed_categories(db_session)
    try:
        result = get_categories_map(db_session)
        assert isinstance(result, dict)
        assert 8001 in result
        assert 8002 in result
        assert result[8001].name == "BatchCatA"
    finally:
        _cleanup(db_session, Category, _TEST_CAT_IDS)


# ── get_user_skills_bulk ──


def test_get_user_skills_bulk_returns_dict(db_session):
    from backend.repositories.learning_repository import get_user_skills_bulk
    result = get_user_skills_bulk(db_session, 2, [1, 999])
    assert isinstance(result, dict)
    assert 1 in result
    assert 999 not in result
    assert hasattr(result[1], "proficiency_level")


def test_get_user_skills_bulk_empty(db_session):
    from backend.repositories.learning_repository import get_user_skills_bulk
    assert get_user_skills_bulk(db_session, 99901, []) == {}


# ── get_completed_step_ids_bulk ──


def test_get_completed_step_ids_bulk_returns_set(db_session):
    from backend.repositories.learning_repository import (
        get_completed_step_ids_bulk,
    )
    result = get_completed_step_ids_bulk(db_session, 2, [1, 999])
    assert isinstance(result, set)
    assert 1 in result
    assert 999 not in result


def test_get_completed_step_ids_bulk_empty(db_session):
    from backend.repositories.learning_repository import (
        get_completed_step_ids_bulk,
    )
    assert get_completed_step_ids_bulk(db_session, 99901, []) == set()
