"""Cascade-matrix + restricted-delete tests (API level).

Pins the exact ON DELETE contract of src/migrations/003_reduced_schema.sql.
Fixture graphs are built through public API flows via
tests/integrity_support.py; persisted state is asserted directly through
db_session. Assessments are the one direct-DB insert (no create endpoint).
"""

from backend.entities.assessment import (
    Assessment, AssessmentQuestion, AssessmentResult,
)
from backend.entities.catalog import (
    Category, JobRoleSkill, Resource, Skill, SkillPrerequisite,
)
from backend.entities.engagement import ActivityLog
from backend.entities.learning import Path, PathStep, StepProgress, UserSkill

from tests.integrity_support import (
    complete_step, constellation, fresh, generate_path, mk_assessment,
    mk_category, mk_job_role, mk_skill, register_user, submit_assessment,
    teardown,
)


def test_bare_skill_deletes_cleanly(api_client, admin_headers, db_session):
    """ERD: a skill with an empty dependent census is not restricted;
    DELETE /admin/skills returns 200 and the skills row is gone."""
    skill = mk_skill(api_client, admin_headers)
    response = api_client.delete(f"/api/admin/skills/{skill}",
                                 headers=admin_headers)
    assert response.status_code == 200, response.text
    db_session.expire_all()
    assert db_session.query(Skill).filter_by(id=skill).count() == 0


def test_blocked_delete_lists_every_counter(api_client, admin_headers,
                                            db_session):
    """ERD: skills are RESTRICT while job_role_skills, user_skills,
    path_steps, resources, assessments or either skill_prerequisites
    direction references them; the 409 census enumerates every relation
    exactly (prerequisites split requires/required_by)."""
    ids = constellation(api_client, admin_headers, db_session)
    try:
        blocked = api_client.delete(f"/api/admin/skills/{ids['skill']}",
                                    headers=admin_headers)
        assert blocked.status_code == 409
        detail = blocked.json()["detail"]
        assert detail["dependents"] == {
            "requires": 1, "required_by": 1, "resources": 1,
            "assessments": 1, "job_role_skills": 1,
            "user_skills": 1, "path_steps": 1}
        assert "force=true" in detail["message"]
    finally:
        teardown(api_client, admin_headers, ids["teardown"])


def test_force_delete_matches_erd_cascade_contract(api_client, admin_headers,
                                                   db_session):
    """ERD under ?force=true: skill_prerequisites (both directions),
    job_role_skills and user_skills CASCADE away; resources.skill_id,
    assessments.skill_id (its questions kept) and path_steps.skill_id
    SET NULL."""
    ids = constellation(api_client, admin_headers, db_session)
    try:
        step_id = ids["path"]["steps"][0]["id"]
        questions = db_session.query(AssessmentQuestion).filter_by(
            assessment_id=ids["assessment"]).count()
        deleted = api_client.delete(
            f"/api/admin/skills/{ids['skill']}?force=true",
            headers=admin_headers)
        assert deleted.status_code == 200, deleted.text
        db_session.expire_all()
        sid = ids["skill"]
        assert db_session.query(SkillPrerequisite).filter(
            (SkillPrerequisite.skill_id == sid) |
            (SkillPrerequisite.prerequisite_id == sid)).count() == 0
        assert db_session.query(JobRoleSkill).filter_by(
            skill_id=sid).count() == 0
        assert db_session.query(UserSkill).filter_by(skill_id=sid).count() == 0
        assert db_session.get(Resource, ids["resource"]).skill_id is None
        assert db_session.get(Assessment, ids["assessment"]).skill_id is None
        assert db_session.query(AssessmentQuestion).filter_by(
            assessment_id=ids["assessment"]).count() == questions
        assert db_session.get(PathStep, step_id).skill_id is None
    finally:
        plan = ids["teardown"]
        teardown(api_client, admin_headers,
                 {**plan, "skills": plan["skills"][1:]})


def test_user_delete_cascades_learning_and_nulls_activity(
        api_client, admin_headers, db_session):
    """ERD: users delete forced-by-design — paths, path_steps,
    step_progress, user_skills and assessment_results CASCADE while
    activity_log.user_id SET NULLs (audit trail survives)."""
    skill = mk_skill(api_client, admin_headers)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    assessment = mk_assessment(db_session, skill)
    try:
        user_id, headers, path = generate_path(api_client, role["title"])
        step_id = path["steps"][0]["id"]
        complete_step(api_client, headers, step_id)
        submit_assessment(api_client, headers, assessment)
        logged = [row.id for row in db_session.query(ActivityLog)
                  .filter_by(user_id=user_id).all()]
        assert logged
        deleted = api_client.delete(f"/api/admin/users/{user_id}",
                                    headers=admin_headers)
        assert deleted.status_code == 200, deleted.text
        db_session.expire_all()
        assert db_session.query(Path).filter_by(user_id=user_id).count() == 0
        assert db_session.get(PathStep, step_id) is None
        assert db_session.query(StepProgress).filter_by(
            user_id=user_id).count() == 0
        assert db_session.query(UserSkill).filter_by(
            user_id=user_id).count() == 0
        assert db_session.query(AssessmentResult).filter_by(
            user_id=user_id).count() == 0
        rows = db_session.query(ActivityLog).filter(
            ActivityLog.id.in_(logged)).all()
        assert len(rows) == len(logged)
        assert all(row.user_id is None for row in rows)
    finally:
        teardown(api_client, admin_headers, {
            "assessments": [assessment], "roles": [role["id"]],
            "skills": [skill]})


def test_assessment_delete_cascades_questions_and_results(
        api_client, admin_headers, db_session):
    """ERD: deleting a missing assessment maps to 404; a real delete
    CASCADEs both assessment_questions and assessment_results away."""
    missing = api_client.delete("/api/admin/assessments/99999999",
                                headers=admin_headers)
    assert missing.status_code == 404
    skill = mk_skill(api_client, admin_headers)
    assessment = mk_assessment(db_session, skill)
    user_id, headers = register_user(api_client)
    submit_assessment(api_client, headers, assessment)
    deleted = api_client.delete(f"/api/admin/assessments/{assessment}",
                                headers=admin_headers)
    assert deleted.status_code == 200, deleted.text
    db_session.expire_all()
    assert db_session.get(Assessment, assessment) is None
    assert db_session.query(AssessmentQuestion).filter_by(
        assessment_id=assessment).count() == 0
    assert db_session.query(AssessmentResult).filter_by(
        assessment_id=assessment).count() == 0
    teardown(api_client, admin_headers, {"users": [user_id],
                                         "skills": [skill]})


def test_path_delete_cascades_steps_and_progress(api_client, admin_headers,
                                                 db_session):
    """ERD: an owned-path delete CASCADEs its path_steps and, with them,
    every step_progress row (first covered success-path delete)."""
    skill = mk_skill(api_client, admin_headers)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    user_id, headers, path = generate_path(api_client, role["title"])
    try:
        step_ids = [s["id"] for s in path["steps"]]
        complete_step(api_client, headers, step_ids[0])
        deleted = api_client.delete(f"/api/paths/{path['id']}",
                                    headers=headers)
        assert deleted.status_code == 200, deleted.text
        db_session.expire_all()
        assert db_session.query(PathStep).filter_by(
            path_id=path["id"]).count() == 0
        assert db_session.query(StepProgress).filter(
            StepProgress.step_id.in_(step_ids)).count() == 0
    finally:
        teardown(api_client, admin_headers, {
            "users": [user_id], "roles": [role["id"]], "skills": [skill]})


def test_category_matrix_leaf_ok_blocks_then_force_detaches(
        api_client, admin_headers, db_session):
    """ERD: an empty category deletes freely (200); one holding skills is
    RESTRICTed behind a {'skills': n} census (409); ?force=true SET NULLs
    skills.category_id and child categories' parent_id (self-FK)."""
    free = mk_category(api_client, admin_headers)
    freed = api_client.delete(f"/api/admin/categories/{free}",
                              headers=admin_headers)
    assert freed.status_code == 200, freed.text
    parent = mk_category(api_client, admin_headers)
    child = mk_category(api_client, admin_headers, parent_id=parent)
    skill = mk_skill(api_client, admin_headers, category_id=parent)
    try:
        blocked = api_client.delete(f"/api/admin/categories/{parent}",
                                    headers=admin_headers)
        assert blocked.status_code == 409
        assert blocked.json()["detail"]["dependents"] == {"skills": 1}
        forced = api_client.delete(
            f"/api/admin/categories/{parent}?force=true",
            headers=admin_headers)
        assert forced.status_code == 200, forced.text
        db_session.expire_all()
        assert db_session.get(Skill, skill).category_id is None
        assert db_session.get(Category, child).parent_id is None
    finally:
        teardown(api_client, admin_headers, {"skills": [skill],
                                             "categories": [child]})


def test_admin_category_edit_roundtrip_preserves_parent(
        api_client, admin_headers, db_session):
    """GET /admin/categories must expose description/parent_id so the
    admin edit dialog prefills them; an edit round-trip echoing
    parent_id keeps the link while an explicit null detaches it.
    Regression for routers/catalog_admin.list_categories; built via
    integrity_support.mk_category + teardown like its siblings."""
    parent = api_client.post("/api/admin/categories", json={
        "name": fresh("Par"), "description": "parent desc"},
        headers=admin_headers).json()
    child = mk_category(api_client, admin_headers, parent_id=parent["id"])
    try:
        listed = {c["id"]: c for c in api_client.get(
            "/api/admin/categories", headers=admin_headers).json()}
        assert listed[child]["parent_id"] == parent["id"]
        assert listed[parent["id"]]["description"] == "parent desc"
        roundtrip = api_client.put(f"/api/admin/categories/{child}", json={
            "name": fresh("Kid"), "description": None,
            "parent_id": parent["id"]}, headers=admin_headers)
        assert roundtrip.status_code == 200, roundtrip.text
        db_session.expire_all()
        assert db_session.get(Category, child).parent_id == parent["id"]
        detached = api_client.put(f"/api/admin/categories/{child}", json={
            "parent_id": None}, headers=admin_headers)
        assert detached.status_code == 200, detached.text
        db_session.expire_all()
        assert db_session.get(Category, child).parent_id is None
    finally:
        teardown(api_client, admin_headers,
                 {"categories": [child, parent["id"]]})


def test_job_role_mappings_restrict_then_force_cascade(
        api_client, admin_headers, db_session):
    """ERD: job_roles are RESTRICT while job_role_skills map them (census
    equals the mapping count); ?force=true CASCADEs the mappings away."""
    first = mk_skill(api_client, admin_headers)
    second = mk_skill(api_client, admin_headers)
    role = mk_job_role(api_client, admin_headers, skill_ids=[first, second])
    blocked = api_client.delete(f"/api/admin/job-roles/{role['id']}",
                                headers=admin_headers)
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["dependents"] == {"job_role_skills": 2}
    forced = api_client.delete(
        f"/api/admin/job-roles/{role['id']}?force=true",
        headers=admin_headers)
    assert forced.status_code == 200, forced.text
    db_session.expire_all()
    assert db_session.query(JobRoleSkill).filter_by(
        job_role_id=role["id"]).count() == 0
    teardown(api_client, admin_headers, {"skills": [first, second]})


def test_duplicate_natural_keys_map_to_client_errors(api_client,
                                                     admin_headers):
    """Behavioral pin: duplicate natural keys on CREATE surface as client
    errors, never 500 — duplicate category name and duplicate job-role
    title keep their pre-existing wire status (400, see
    routers/catalog_admin._fail_create)."""
    category = api_client.post("/api/admin/categories", json={
        "name": fresh("DupCat")}, headers=admin_headers).json()
    role = api_client.post("/api/admin/job-roles", json={
        "title": fresh("DupRole")}, headers=admin_headers).json()
    dup_cat = api_client.post("/api/admin/categories", json={
        "name": category["name"]}, headers=admin_headers)
    dup_role = api_client.post("/api/admin/job-roles", json={
        "title": role["title"]}, headers=admin_headers)
    assert dup_cat.status_code == 400, dup_cat.text
    assert dup_role.status_code == 400, dup_role.text
    teardown(api_client, admin_headers, {"roles": [role["id"]],
                                         "categories": [category["id"]]})


def test_step_progress_double_complete_keeps_one_pk_row(
        api_client, admin_headers, db_session):
    """ERD: step_progress PK (user_id, step_id) makes completions
    idempotent — completing the same step twice returns 200 twice and
    keeps exactly one row with completed_at stamped once."""
    skill = mk_skill(api_client, admin_headers)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    user_id, headers, path = generate_path(api_client, role["title"])
    try:
        step_id = path["steps"][0]["id"]
        first = complete_step(api_client, headers, step_id)
        second = complete_step(api_client, headers, step_id)
        assert first["completed_at"] == second["completed_at"]
        db_session.expire_all()
        assert db_session.query(StepProgress).filter_by(
            user_id=user_id, step_id=step_id).count() == 1
    finally:
        teardown(api_client, admin_headers, {
            "users": [user_id], "roles": [role["id"]], "skills": [skill]})
