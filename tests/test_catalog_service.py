"""Focused tests for catalog_service._serialize_category.

Use seeded data only (no commits) so the shared session DB stays pristine for
the stable-catalog-counts test. The empty-skills case creates + deletes a
throwaway category inside try/finally to leave no net residue."""

from backend.entities.catalog import Category
from backend.repositories import catalog_repository as crepo
from backend.services import catalog_service as svc


def test_serialize_category_returns_fields_and_filtered_skills(db_session):
    categories = crepo.get_all_categories(db_session)
    target = None
    other = None
    for c in categories:
        if len(crepo.get_skills_by_category(db_session, c.id)) >= 2:
            target = c
            for c2 in categories:
                if c2.id != c.id:
                    other = c2
                    break
            break
    assert target is not None, "seed must contain a category with >=2 skills"

    result = svc._serialize_category(db_session, target)
    assert result["id"] == target.id
    assert result["name"] == target.name
    assert result["parent_id"] == target.parent_id

    returned_ids = {s["id"] for s in result["skills"]}
    expected_ids = {s.id for s in crepo.get_skills_by_category(db_session, target.id)}
    assert returned_ids == expected_ids
    assert all(s["category_id"] == target.id for s in result["skills"])
    if other is not None:
        other_ids = {s.id for s in crepo.get_skills_by_category(db_session, other.id)}
        assert not (returned_ids & other_ids)


def test_serialize_category_empty_skills(db_session):
    cat = Category(name="CatEmpty_tmp_3_6", description="tmp", parent_id=None)
    db_session.add(cat)
    db_session.flush()
    db_session.commit()
    try:
        result = svc._serialize_category(db_session, cat)
        assert result["id"] == cat.id
        assert result["skills"] == []
    finally:
        db_session.delete(cat)
        db_session.commit()
