"""tests/test_question_bank.py — seeded-bank quiz delivery (deterministic)."""
import pytest

from backend.services import question_bank
from backend.services.assess_service import normalize_key
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository


def _role_with_skills(db_session):
    """Return a (role_title, skill ids) pair where the role has >= 2 skills."""
    roles = catalog_repository.get_all_job_roles(db_session)
    for role in roles:
        ids = catalog_repository.get_job_role_skill_ids(db_session, role.id)
        if len(ids) >= 2:
            return role.title, ids
    raise AssertionError("no seeded role with >= 2 skills")


def test_role_quiz_bank_covers_all_skills_with_matching_ids(db_session):
    """Every role skill yields seeded questions with exact _q<i> id shapes."""
    role_title, ids = _role_with_skills(db_session)
    skills = catalog_repository.get_skills_by_ids(db_session, ids)
    assessments = arepo.get_assessments_for_skills(db_session, ids)

    result = question_bank.role_quiz_bank(db_session, role_title)
    assert result["skills"] and result["questions"]

    names_by_id = {s.name: s for s in skills}
    for q in result["questions"]:
        skill = names_by_id.get(q["skill"])
        assert skill is not None, f"unknown skill {q['skill']}"
        assert q["id"] == f"{normalize_key(q['skill']).lower()}_q0" or \
            q["id"].startswith(f"{normalize_key(q['skill']).lower()}_q")
        assert q["text"] and isinstance(q["options"], list) and q["options"]

    per_skill: dict[str, list] = {}
    for q in result["questions"]:
        per_skill.setdefault(q["skill"], []).append(q)
    for sid, s in zip(ids, skills):
        expected_n = len(arepo.get_questions(db_session, assessments[sid].id))
        got = per_skill.get(s.name, [])
        assert len(got) == expected_n, \
            f"{s.name}: expected {expected_n} questions, got {len(got)}"
        expected_ids = [f"{normalize_key(s.name).lower()}_q{i}"
                        for i in range(expected_n)]
        assert [q["id"] for q in got] == expected_ids


def test_role_quiz_bank_unknown_role_returns_empty(db_session):
    """Unknown role title yields an empty payload without raising."""
    result = question_bank.role_quiz_bank(db_session, "No Such Role")
    assert result == {"questions": [], "skills": []}


def test_skill_quiz_bank_includes_assessment_id(db_session):
    """Single-skill bank returns its seed assessment_id for submit reuse."""
    skills = catalog_repository.get_all_skills(db_session)
    assert skills
    sid = skills[0].id
    result = question_bank.skill_quiz_bank(db_session, sid)
    assert result["assessment_id"] is not None
    assert result["skill_id"] == sid
    assert result["skill"] == skills[0].name
    assert result["questions"]
    for q in result["questions"]:
        assert q["id"].startswith(f"{normalize_key(q['skill']).lower()}_q")
        assert q["options"]


def test_skill_quiz_bank_unknown_skill_empty(db_session):
    """Unknown skill_id yields an empty payload (assessment_id None)."""
    result = question_bank.skill_quiz_bank(db_session, 999999)
    assert result["assessment_id"] is None
    assert result["questions"] == []
    assert result["skill"] is None
