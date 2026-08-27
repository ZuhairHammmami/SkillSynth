import pytest

from backend.entities.catalog import Category, Skill
from backend.repositories import catalog_repository as crepo


def test_get_skills_by_category_filters_and_excludes(db_session):
    """Only skills whose category_id matches are returned; others excluded."""
    cat_a = Category(name="cat_acat", description="A")
    cat_b = Category(name="cat_bcat", description="B")
    db_session.add_all([cat_a, cat_b])
    db_session.flush()

    s_a1 = Skill(name="skill_a1", category_id=cat_a.id, difficulty_level=1,
                 estimated_hours=1)
    s_a2 = Skill(name="skill_a2", category_id=cat_a.id, difficulty_level=1,
                 estimated_hours=1)
    s_b1 = Skill(name="skill_b1", category_id=cat_b.id, difficulty_level=1,
                 estimated_hours=1)
    db_session.add_all([s_a1, s_a2, s_b1])
    db_session.commit()

    result = crepo.get_skills_by_category(db_session, cat_a.id)
    ids = {s.id for s in result}
    assert ids == {s_a1.id, s_a2.id}
    assert s_b1.id not in ids
