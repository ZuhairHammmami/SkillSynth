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
        assert len(data["nodes"]) == 102
        assert len(data["categories"]) == 16
        assert len(data["edges"]) == 112

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
        paths = response.json()
        assert isinstance(paths, list)
        assert len(paths) == 2

    def test_get_path_detail(self, api_client, auth_headers):
        paths = api_client.get("/api/paths/", headers=auth_headers).json()
        detail = api_client.get(f"/api/paths/{paths[0]['id']}",
                                headers=auth_headers)
        assert detail.status_code == 200
        assert "steps" in detail.json()
        assert isinstance(detail.json()["id"], int)

    def test_get_path_not_found(self, api_client, auth_headers):
        assert api_client.get("/api/paths/99999", headers=auth_headers).status_code == 404

    def test_update_path(self, api_client, auth_headers):
        paths = api_client.get("/api/paths/", headers=auth_headers).json()
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
