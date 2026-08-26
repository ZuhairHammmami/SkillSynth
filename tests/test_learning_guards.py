"""Learning guardrail tests — split from test_learning.py to honor the
300-line file cap. Covers cross-user 404 enforcement (paths/steps),
wizard mastery exclusion (proficiency >= 3 omitted from generated plans),
prerequisite topological ordering of generated steps, and the
/api/learning/generate alias parity with /api/generate-path/."""

from backend.entities.catalog import Skill, SkillPrerequisite

from tests.integrity_support import (
    generate_path, mk_job_role, mk_skill, register_user, teardown,
)


def _wizard_payload(role_title):
    """Canonical wizard body shared by alias/canonical parity checks;
    consumed by TestGenerateAliasParity and TestWizardMasteryExclusion."""
    return {"goal": role_title, "weekly_hours": 10,
            "preferences": {}, "answers": {}}


class TestOwnershipEnforcement:
    """Another user's path/step is invisible: every owned-resource route
    (routers/paths.py get/update/delete + learning_service.complete_step's
    owner-scoped path lookup) answers 404, never leaking existence."""

    def test_other_users_path_and_step_ops_are_404(
            self, api_client, admin_headers):
        skill = mk_skill(api_client, admin_headers)
        role = mk_job_role(api_client, admin_headers, skill_ids=[skill])
        owner_id, owner_headers, path = generate_path(api_client, role["title"])
        intruder_id, intruder_headers = register_user(api_client)
        try:
            step_id = path["steps"][0]["id"]
            hijack = api_client.put(f"/api/paths/{path['id']}",
                                    json={"title": "Hijacked"},
                                    headers=intruder_headers)
            assert hijack.status_code == 404, hijack.text
            assert api_client.get(f"/api/paths/{path['id']}",
                                  headers=intruder_headers).status_code == 404
            assert api_client.delete(f"/api/paths/{path['id']}",
                                     headers=intruder_headers).status_code == 404
            assert api_client.post(f"/api/steps/{step_id}/complete",
                                   headers=intruder_headers).status_code == 404
            assert api_client.post(f"/api/steps/{step_id}/undo-complete",
                                   headers=intruder_headers).status_code == 404
            intact = api_client.get(f"/api/paths/{path['id']}",
                                    headers=owner_headers).json()
            assert intact["title"] == path["title"]
        finally:
            teardown(api_client, admin_headers, {
                "users": [owner_id, intruder_id], "roles": [role["id"]],
                "skills": [skill]})


class TestWizardMasteryExclusion:
    """learning_service.generate_path filters plan skills by
    levels < MASTERY_LEVEL (3) before topo-sorting, so a learner already
    at proficiency >= 3 on a role-mapped skill gets no step for it."""

    def test_mastered_skill_omitted_from_generated_steps(
            self, api_client, admin_headers, db_session):
        from backend.repositories import assess_repository as arepo
        mastered = mk_skill(api_client, admin_headers)
        pending = mk_skill(api_client, admin_headers)
        role = mk_job_role(api_client, admin_headers,
                           skill_ids=[mastered, pending])
        user_id, headers = register_user(api_client)
        arepo.upsert_user_skill(db_session, user_id, mastered, 3)
        db_session.commit()
        try:
            generated = api_client.post(
                "/api/generate-path/", json=_wizard_payload(role["title"]),
                headers=headers)
            assert generated.status_code == 200, generated.text
            mastered_name = db_session.get(Skill, mastered).name
            pending_name = db_session.get(Skill, pending).name
            titles = [s["title"] for s in generated.json()["steps"]]
            assert f"Master {mastered_name}" not in titles
            assert f"Master {pending_name}" in titles
        finally:
            teardown(api_client, admin_headers, {
                "users": [user_id], "roles": [role["id"]],
                "skills": [mastered, pending]})


class TestPrerequisiteOrdering:
    """Generated steps respect Kahn topological order over
    skill_prerequisites (_order_by_prereqs): prerequisites precede their
    dependents even when the job-role mapping lists them reversed."""

    def test_generated_steps_respect_topological_order(
            self, api_client, admin_headers, db_session):
        base = mk_skill(api_client, admin_headers)
        advanced = mk_skill(api_client, admin_headers,
                            prerequisite_ids=[base])
        role = mk_job_role(api_client, admin_headers,
                           skill_ids=[advanced, base])
        user_id, headers, path = generate_path(api_client, role["title"])
        try:
            names = [s["title"].removeprefix("Master ")
                     for s in path["steps"]]
            positions = {name: i for i, name in enumerate(names)}
            assert positions[db_session.get(Skill, base).name] \
                < positions[db_session.get(Skill, advanced).name]
            edges = db_session.query(SkillPrerequisite).filter(
                SkillPrerequisite.skill_id.in_([base, advanced])).all()
            for edge in edges:
                prereq_name = db_session.get(Skill, edge.prerequisite_id).name
                dependent_name = db_session.get(Skill, edge.skill_id).name
                assert positions[prereq_name] < positions[dependent_name]
        finally:
            teardown(api_client, admin_headers, {
                "users": [user_id], "roles": [role["id"]],
                "skills": [base, advanced]})


class TestGenerateAliasParity:
    """/api/learning/generate delegates to paths.generate_path via
    routers/learning.generate_path_alias: same learner + payload through
    both URLs → identical status, wire key set and int path id."""

    def test_alias_behaves_identically_to_canonical(self, api_client):
        user_id, headers = register_user(api_client)
        canonical = api_client.post("/api/generate-path/", json=_wizard_payload(
            "Data Scientist"), headers=headers)
        alias = api_client.post("/api/learning/generate", json=_wizard_payload(
            "Data Scientist"), headers=headers)
        assert canonical.status_code == alias.status_code == 200, alias.text
        assert set(canonical.json()) == set(alias.json())
        assert isinstance(alias.json()["id"], int)
        assert isinstance(canonical.json()["id"], int)
        assert alias.json()["steps"] and canonical.json()["steps"]
