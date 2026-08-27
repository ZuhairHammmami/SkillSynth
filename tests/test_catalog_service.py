"""Focused tests for catalog_service._serialize_category."""

from backend.entities.catalog import Category, Skill
from backend.services import catalog_service as svc


def _make_category(db, name):
    """Insert a Category row and return it (uncommitted flush id)."""
    cat = Category(name=name, description=f"{name} desc", parent_id=None)
    db.add(cat)
    db.flush()
    return cat


def _make_skill(db, name, category_id):
    """Insert a Skill row bound to category_id; returns the row."""
    skill = Skill(name=name, description=f"{name} desc", difficulty_level=5,
                  estimated_hours=10, category_id=category_id)
    db.add(skill)
    db.flush()
    return skill


def test_serialize_category_returns_fields_and_filtered_skills(db_session):
    cat_a = _make_category(db_session, "CatA_3_3")
    cat_b = _make_category(db_session, "CatB_3_3")
    db_session.commit()

    s_a1 = _make_skill(db_session, "SkillA1_3_3", cat_a.id)
    s_a2 = _make_skill(db_session, "SkillA2_3_3", cat_a.id)
    s_b1 = _make_skill(db_session, "SkillB1_3_3", cat_b.id)
    db_session.commit()

    result = svc._serialize_category(db_session, cat_a)

    assert result["id"] == cat_a.id
    assert result["name"] == "CatA_3_3"
    assert result["description"] == "CatA_3_3 desc"
    assert result["parent_id"] is None
    returned_ids = {s["id"] for s in result["skills"]}
    assert returned_ids == {s_a1.id, s_a2.id}
    assert s_b1.id not in returned_ids
    assert all(set(["id", "name", "category_id"]) <= set(s)
               for s in result["skills"])


def test_serialize_category_empty_skills(db_session):
    cat = _make_category(db_session, "CatEmpty_3_3")
    db_session.commit()

    result = svc._serialize_category(db_session, cat)
    assert result["id"] == cat.id
    assert result["skills"] == []
