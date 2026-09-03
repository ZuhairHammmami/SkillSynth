"""Tests for in-memory TTL cache invalidation on catalog writes."""


def test_cache_invalidation_on_skill_update():
    from backend.services.catalog_service import _skill_cache, invalidate_skill_cache
    _skill_cache[1] = {"name": "old"}
    invalidate_skill_cache(1)
    assert 1 not in _skill_cache


def test_cache_clears_all_skills_on_delete():
    from backend.services.catalog_service import _skill_cache, invalidate_skill_cache
    _skill_cache[1] = {"name": "a"}
    _skill_cache[2] = {"name": "b"}
    invalidate_skill_cache()
    assert len(_skill_cache) == 0


def test_cache_clears_category_on_any_write():
    from backend.services.catalog_service import _category_cache, invalidate_skill_cache
    _category_cache["all"] = ["data"]
    invalidate_skill_cache()
    assert len(_category_cache) == 0


def test_cache_clears_prereq_graph_on_write():
    from backend.services.catalog_service import _prereq_graph_cache, invalidate_skill_cache
    _prereq_graph_cache["graph"] = {1: [2, 3]}
    invalidate_skill_cache()
    assert len(_prereq_graph_cache) == 0


def test_cache_clears_job_roles_on_write():
    from backend.services.catalog_service import _job_role_cache, invalidate_skill_cache
    _job_role_cache[1] = {"title": "Engineer"}
    invalidate_skill_cache()
    assert len(_job_role_cache) == 0


def test_partial_invalidation_preserves_other_entries():
    from backend.services.catalog_service import _skill_cache, invalidate_skill_cache
    _skill_cache[1] = {"name": "a"}
    _skill_cache[2] = {"name": "b"}
    invalidate_skill_cache(1)
    assert 1 not in _skill_cache
    assert 2 in _skill_cache


def test_invalidate_nonexistent_key_no_error():
    from backend.services.catalog_service import _skill_cache, invalidate_skill_cache
    _skill_cache.clear()
    invalidate_skill_cache(9999)
    assert len(_skill_cache) == 0
