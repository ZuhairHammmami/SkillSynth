"""Learning tests — graph, gaps, path generation, path CRUD, step progress."""

import uuid

import pytest


def _fresh_email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.com"


class TestLearningGraph:

    def test_graph_public(self, api_client):
        response = api_client.get("/api/learning/graph")
        assert response.status_code == 200
        data = response.json()
        assert set(data) == {"nodes", "edges", "categories"}
        assert len(data["nodes"]) == 152
        assert len(data["categories"]) == 16
        assert len(data["edges"]) == 269

    def test_gaps(self, api_client, auth_headers):
        response = api_client.get("/api/learning/gaps",
                                  params={"target_role": "Frontend Developer"},
                                  headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) == {"goal_skills", "gaps"}
        assert len(data["gaps"]) == len(data["goal_skills"])

    def test_gaps_unknown_role(self, api_client, auth_headers):
        response = api_client.get("/api/learning/gaps",
                                  params={"target_role": "NonexistentRole"},
                                  headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["gaps"] == []


class TestPaths:

    def test_list_paths(self, api_client, auth_headers):
        response = api_client.get("/api/paths/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert data["total"] == 2

    def test_get_path_detail(self, api_client, auth_headers):
        paths = api_client.get("/api/paths/", headers=auth_headers).json()["items"]
        detail = api_client.get(f"/api/paths/{paths[0]['id']}",
                                headers=auth_headers)
        assert detail.status_code == 200
        assert "steps" in detail.json()
        assert isinstance(detail.json()["id"], int)

    def test_get_path_not_found(self, api_client, auth_headers):
        assert api_client.get("/api/paths/99999", headers=auth_headers).status_code == 404

    def test_update_path(self, api_client, auth_headers):
        paths = api_client.get("/api/paths/", headers=auth_headers).json()["items"]
        update = api_client.put(f"/api/paths/{paths[0]['id']}", json={
            "title": "Updated Path Title",
        }, headers=auth_headers)
        assert update.status_code == 200
        assert update.json()["title"] == "Updated Path Title"

    def test_delete_path_not_found(self, api_client, auth_headers):
        assert api_client.delete("/api/paths/99999", headers=auth_headers).status_code == 404


class TestGeneratePath:

    def test_generate_path(self, api_client):
        email = _fresh_email("gen")
        api_client.post("/api/auth/register", json={
            "email": email, "password": "GenPass@123",
        })
        token = api_client.post("/api/auth/token", data={
            "username": email, "password": "GenPass@123",
        }).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.post("/api/generate-path/", json={
            "goal": "Data Scientist", "weekly_hours": 10,
            "preferences": {}, "answers": {},
        }, headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data["id"], int)
        assert data["steps"]

    def test_generate_path_unknown_role(self, api_client, auth_headers):
        response = api_client.post("/api/generate-path/", json={
            "goal": "NonexistentRole", "weekly_hours": 10,
            "preferences": {}, "answers": {},
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_generate_path_requires_auth(self, api_client):
        response = api_client.post("/api/generate-path/", json={
            "goal": "Data Scientist", "weekly_hours": 10, "preferences": {},
        })
        assert response.status_code == 401


class TestLeveledGeneration:

    def test_levels_set_selected_and_current(self, api_client, db_session):
        """Per-skill levels flow into selected_level/current_level on steps
        and are echoed in the response `levels` mapping."""
        from backend.dto.learning import DetailedPreferences, GeneratePathIn
        from backend.entities.identity import User
        from backend.repositories import catalog_repository as crepo
        from backend.repositories import learning_repository as lrepo
        from backend.services import learning_service as ls

        email = _fresh_email("lvl")
        api_client.post("/api/auth/register", json={
            "email": email, "password": "LvlPass@123"})
        api_client.post("/api/auth/token", data={
            "username": email, "password": "LvlPass@123"})
        user = db_session.query(User).filter_by(email=email).first()
        assert user is not None

        role = crepo.get_job_role_by_title(db_session, "Data Scientist")
        skills = crepo.get_skills_by_ids(
            db_session, crepo.get_job_role_skill_ids(db_session, role.id))
        assert skills
        target = skills[0]
        data = GeneratePathIn(
            goal="Data Scientist", weekly_hours=10,
            preferences=DetailedPreferences(), answers={},
            levels={target.name: 4})
        detail, err = ls.generate_path(db_session, user, data)
        assert err is None, err

        steps = lrepo.get_steps(db_session, detail["id"])
        matched = [s for s in steps if s.skill_id == target.id]
        assert matched, "expected a step for the leveled goal skill"
        assert matched[0].selected_level == 4
        assert matched[0].current_level == 4
        assert detail["levels"][target.name] == 4

    def test_pick_resource_ids_accepts_format_list(self, db_session):
        """format as a list accepts resources whose type is in the list; a
        single-string exact match still excludes mismatched types."""
        from backend.repositories import catalog_repository as crepo
        from backend.services import learning_service as ls

        skill = crepo.get_all_skills(db_session)[0]
        sample = crepo.get_all_resources(db_session)[0]
        rt = sample.type
        other = "nonexistent_type_xyz"
        prefs = {"is_free": False, "language": sample.language,
                 "format": [rt, other]}
        listed = ls._pick_resource_ids(db_session, skill, prefs)
        assert sample.id in listed
        exact = ls._pick_resource_ids(
            db_session, skill, {"is_free": False,
                               "language": sample.language, "format": other})
        assert sample.id not in exact


class TestStepProgress:

    def test_complete_and_undo_step(self, api_client, auth_headers):
        before = api_client.get("/api/progress/dashboard",
                                headers=auth_headers).json()
        target = None
        for path in before["paths"]:
            for step in path["steps"]:
                if not step["is_completed"]:
                    target = step
                    break
            if target:
                break
        assert target is not None
        complete = api_client.post(f"/api/steps/{target['id']}/complete",
                                   headers=auth_headers)
        assert complete.status_code == 200
        assert complete.json()["step_id"] == target["id"]
        undo = api_client.post(f"/api/steps/{target['id']}/undo-complete",
                               headers=auth_headers)
        assert undo.status_code == 200
        after = api_client.get("/api/progress/dashboard",
                               headers=auth_headers).json()
        assert after["completed_steps"] == before["completed_steps"]

    def test_complete_step_not_found(self, api_client, auth_headers):
        response = api_client.post("/api/steps/99999/complete", headers=auth_headers)
        assert response.status_code == 404

    def test_progress_dashboard(self, api_client, auth_headers):
        response = api_client.get("/api/progress/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_paths"] == 2
        assert data["total_steps"] == 17
        assert data["completed_steps"] == 7
        assert data["completion_percentage"] == 41.2
        assert set(data) >= {
            "total_paths", "total_steps", "completed_steps",
            "completion_percentage", "remaining_hours", "total_hours",
        }


def test_learning_analysis_payload(api_client, auth_headers):
    """GET /learning/analysis returns the frozen weaknesses payload keys.

    Consumed by frontend useWeaknesses (Task 10b); delegates to
    analytics_service.analyze_weaknesses.
    """
    r = api_client.get("/api/learning/analysis", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert {"weaknesses", "strengths", "recommended_focus",
            "average_assessment_score"} <= set(body)


class TestWizardScoringNoDowngrade:

    def test_empty_answers_do_not_downgrade_proficiency(
            self, api_client, user_token, db_session):
        """Regression: regenerating a path with no wizard answers must not
        zero existing user_skills (final-review Critical finding)."""
        from backend.entities.catalog import Skill
        from backend.repositories import assess_repository as arepo

        assessment = arepo.get_all_assessments(db_session)[0]
        skill = db_session.query(Skill).get(assessment.skill_id)
        assert skill is not None
        arepo.upsert_user_skill(db_session, 4, skill.id, 5)  # veteran id=4
        db_session.commit()

        response = api_client.post("/api/generate-path/", json={
            "goal": "Frontend Developer", "weekly_hours": 10,
            "preferences": {}, "answers": {},
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200, response.text

        level = arepo.get_skill_profile(db_session, 4).get(skill.name)
        assert level == 5, f"proficiency was downgraded to {level}"
