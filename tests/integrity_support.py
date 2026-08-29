"""Fixture-graph builders for tests/test_integrity.py.

Every helper drives PUBLIC API flows only (register/login, admin CRUD,
path generation, step completion, assessment submission) except
mk_assessment — assessments expose no create endpoint, so that one
inserts directly via db_session. teardown() removes every created row
because tests/test_schema.py pins exact seed counts for eight tables.
"""

import uuid

PASSWORD = "Zephyr#7781kq"


def fresh(prefix):
    """Unique-name maker so fixtures never collide with seeded rows."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def register_user(api_client):
    """Register + login a fresh learner; returns (user_id, headers).
    Called by generate_path and the assessment-cascade scenario; the
    login writes the activity_log row the user-delete SET NULL test pins."""
    email = f"{fresh('learner')}@test.com"
    created = api_client.post("/api/auth/register",
                              json={"email": email, "password": PASSWORD})
    assert created.status_code == 200, created.text
    token = api_client.post("/api/auth/token", data={
        "username": email, "password": PASSWORD}).json()["access_token"]
    return created.json()["id"], {"Authorization": f"Bearer {token}"}


def mk_category(api_client, headers, parent_id=None):
    """POST a throwaway category (optionally nested); returns its id."""
    response = api_client.post("/api/admin/categories", json={
        "name": fresh("Cat"), "parent_id": parent_id}, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


def mk_skill(api_client, headers, category_id=None, prerequisite_ids=None):
    """POST a throwaway skill with optional links; returns its id."""
    body = {"name": fresh("Skill")}
    if category_id:
        body["category_id"] = category_id
    if prerequisite_ids:
        body["prerequisite_ids"] = prerequisite_ids
    response = api_client.post("/api/admin/skills", json=body, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


def mk_resource(api_client, headers, skill_id):
    """POST a resource attached to one skill; returns its id."""
    response = api_client.post("/api/admin/resources", json={
        "title": fresh("Res"), "url": "https://example.com/x",
        "type": "article", "skill_id": skill_id}, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


def mk_job_role(api_client, headers, skill_ids=None):
    """POST a job role mapped to skill_ids; returns its payload dict."""
    response = api_client.post("/api/admin/job-roles", json={
        "title": fresh("Role"), "skill_ids": skill_ids or []},
        headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def mk_assessment(db_session, skill_id, n_questions=2):
    """Insert an assessment + n quiz rows directly (no public create
    endpoint); returns the assessment id for submission scenarios."""
    from backend.entities.assessment import Assessment, AssessmentQuestion
    assessment = Assessment(skill_id=skill_id, title=fresh("Quiz"),
                            pass_score=60)
    db_session.add(assessment)
    db_session.flush()
    for i in range(n_questions):
        db_session.add(AssessmentQuestion(
            assessment_id=assessment.id, position=i, prompt=f"Q{i}?",
            options=["alpha", "beta"], correct_index=0))
    db_session.commit()
    return assessment.id


def generate_path(api_client, role_title):
    """Fresh learner + wizard generation toward role_title; returns
    (user_id, headers, path detail). Generation upserts the learner's
    user_skills row (level 0) and one path_steps row per plan skill."""
    user_id, headers = register_user(api_client)
    generated = api_client.post("/api/generate-path/", json={
        "goal": role_title, "weekly_hours": 10,
        "preferences": {}, "answers": {}}, headers=headers)
    assert generated.status_code == 200, generated.text
    return user_id, headers, generated.json()


def constellation(api_client, admin_headers, db_session):
    """One skill referenced by all six dependent relations at once;
    consumed by the skill-delete census and force-cascade tests. Builds
    category→skill, requires/required_by edges, resource, job-role
    mapping, direct-DB assessment, learner path + user_skills row."""
    category = mk_category(api_client, admin_headers)
    prereq_skill = mk_skill(api_client, admin_headers)
    skill = mk_skill(api_client, admin_headers, category_id=category,
                     prerequisite_ids=[prereq_skill])
    blocker = mk_skill(api_client, admin_headers, prerequisite_ids=[skill])
    resource = mk_resource(api_client, admin_headers, skill)
    role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
    assessment = mk_assessment(db_session, skill)
    user_id, headers, path = generate_path(api_client, role["title"])
    return {"category": category, "skill": skill, "prereq_skill": prereq_skill,
            "blocker": blocker, "resource": resource, "role": role["id"],
            "assessment": assessment, "user_id": user_id, "path": path,
            "teardown": {"users": [user_id], "assessments": [assessment],
                         "resources": [resource], "roles": [role["id"]],
                         "skills": [skill, blocker, prereq_skill],
                         "categories": [category]}}


def teardown(api_client, admin_headers, plan):
    """Best-effort fixture cleanup so later suites see exact seed counts
    (test_schema.py pins eight table totals); stale 404s are ignored."""
    routes = [("users", "/api/admin/users/{id}", True),
              ("assessments", "/api/admin/assessments/{id}", True),
              ("resources", "/api/admin/resources/{id}", True),
              ("roles", "/api/admin/job-roles/{id}", True),
              ("skills", "/api/admin/skills/{id}", True),
              ("categories", "/api/admin/categories/{id}", True)]
    for key, template, force in routes:
        for row_id in plan.get(key, []):
            suffix = "?force=true" if force else ""
            api_client.delete(template.format(id=row_id) + suffix,
                              headers=admin_headers)


def complete_step(api_client, headers, step_id):
    """POST one step completion; asserts 200 and returns the payload."""
    response = api_client.post(f"/api/steps/{step_id}/complete",
                               headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def submit_assessment(api_client, headers, assessment_id, n=2):
    """Submit an all-correct attempt; asserts 200 and returns payload."""
    response = api_client.post("/api/assessments/submit", json={
        "assessment_id": assessment_id, "answers": [0] * n}, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()
