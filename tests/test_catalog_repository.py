import pytest

from backend.repositories import catalog_repository as crepo


def test_get_skills_by_category_filters_and_excludes(db_session):
    """Only skills whose category_id matches are returned; others excluded.

    Uses seeded data only (no commits) so the shared session DB stays pristine
    for the stable-catalog-counts test."""
    categories = crepo.get_all_categories(db_session)
    assert len(categories) >= 2

    target = None
    other = None
    for c in categories:
        if crepo.get_skills_by_category(db_session, c.id):
            target = c
            for c2 in categories:
                if c2.id != c.id:
                    other = c2
                    break
            break
    assert target is not None, "seed must contain a category with skills"

    result = crepo.get_skills_by_category(db_session, target.id)
    ids = {s.id for s in result}
    assert ids
    assert all(s.category_id == target.id for s in result)
    if other is not None:
        other_ids = {s.id for s in crepo.get_skills_by_category(db_session, other.id)}
        assert not (ids & other_ids)
