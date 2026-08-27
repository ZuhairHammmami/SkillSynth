"""API-layer tests for leveled step tests + path step level exposure (2.7).

Covers: POST /api/generate-path/ forwarding `levels`; GET /api/paths/{id}
serializing selected_level/current_level; POST /api/steps/{id}/test returning
`level`/`difficulty`; POST /api/steps/{id}/test/submit returning next_level/
level_passed and persisting next_level onto PathStep.current_level.
"""

from backend.entities.catalog import Skill
from backend.entities.learning import PathStep

from tests.integrity_support import (
    generate_path, mk_assessment, mk_job_role, mk_skill, register_user,
    teardown,
)


def _skill_name(db_session, skill_id):
    """Resolve a created skill's name for the `levels` wizard key."""
    return db_session.get(Skill, skill_id).name


def test_generate_path_forwards_levels_and_serializes_them(
        api_client, admin_headers, db_session):
    """Generate with levels; fetched path steps expose selected/current."""
    skill = mk_skill(api_client, admin_headers)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    skill_name = _skill_name(db_session, skill)
    user_id, headers = register_user(api_client)
    generated = api_client.post("/api/generate-path/", json={
        "goal": role["title"], "weekly_hours": 10, "preferences": {},
        "answers": {}, "levels": {skill_name: 4}}, headers=headers)
    assert generated.status_code == 200, generated.text
    detail = generated.json()
    assert detail["steps"], "expected at least one step"
    step = detail["steps"][0]
    assert step["selected_level"] == 4
    assert step["current_level"] == 4
    fetched = api_client.get(f"/api/paths/{detail['id']}", headers=headers).json()
    fstep = fetched["steps"][0]
    assert fstep["selected_level"] == 4
    assert fstep["current_level"] == 4
    teardown(api_client, admin_headers, {
        "users": [user_id], "roles": [role["id"]], "skills": [skill]})


def test_step_test_endpoint_exposes_level_and_difficulty(
        api_client, admin_headers, db_session):
    """Generated step test payload carries level + difficulty fields."""
    skill = mk_skill(api_client, admin_headers)
    assessment = mk_assessment(db_session, skill, n_questions=3)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    user_id, headers, path = generate_path(api_client, role["title"])
    step_id = path["steps"][0]["id"]
    resp = api_client.post(f"/api/steps/{step_id}/test", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "level" in body and "difficulty" in body
    assert isinstance(body["level"], int)
    assert isinstance(body["difficulty"], int)
    teardown(api_client, admin_headers, {
        "users": [user_id], "roles": [role["id"]],
        "skills": [skill], "assessments": [assessment]})


def test_step_grade_persists_next_level(
        api_client, admin_headers, db_session):
    """Grading returns next_level/level_passed and updates step.current_level."""
    skill = mk_skill(api_client, admin_headers)
    assessment = mk_assessment(db_session, skill, n_questions=3)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    user_id, headers, path = generate_path(api_client, role["title"])
    step_id = path["steps"][0]["id"]
    test = api_client.post(f"/api/steps/{step_id}/test", headers=headers).json()
    answers = {str(q["id"]): q["correct_index"] for q in test["questions"]}
    graded = api_client.post(
        f"/api/steps/{step_id}/test/submit",
        json={"assessment_id": test["assessment_id"], "answers": answers},
        headers=headers)
    assert graded.status_code == 200, graded.text
    result = graded.json()
    assert "next_level" in result and "level_passed" in result
    db_step = db_session.get(PathStep, step_id)
    assert db_step.current_level == result["next_level"]
    teardown(api_client, admin_headers, {
        "users": [user_id], "roles": [role["id"]],
        "skills": [skill], "assessments": [assessment]})
