"""Assessment tests — question payload shape and scored submissions."""

import pytest


class TestQuestions:

    def test_questions_shape(self, api_client, auth_headers):
        graph = api_client.get("/api/learning/graph").json()
        html = next(n for n in graph["nodes"] if n["name"] == "HTML")
        response = api_client.get(f"/api/assessments/{html['id']}/questions",
                                  headers=auth_headers)
        assert response.status_code == 200
        questions = response.json()
        assert isinstance(questions, list)
        assert len(questions) == 5
        assert set(questions[0]) == {"id", "skill", "text", "options"}

    def test_questions_unknown_skill(self, api_client, auth_headers):
        response = api_client.get("/api/assessments/99999/questions",
                                  headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_questions_requires_auth(self, api_client):
        response = api_client.get("/api/assessments/1/questions")
        assert response.status_code == 401


class TestSubmit:

    def test_submit_updates_user_skill(self, api_client, auth_headers, admin_headers):
        assessments = api_client.get("/api/admin/assessments",
                                     headers=admin_headers).json()
        html = next(a for a in assessments if a["title"] == "HTML Assessment")
        response = api_client.post("/api/assessments/submit", json={
            "assessment_id": html["id"], "answers": [0, 1, 0, 0, 0],
        }, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["score"] == 100
        assert data["passed"] is True
        assert data["total_questions"] == 5
        me = api_client.get("/api/auth/me", headers=auth_headers).json()
        assert me["skill_profile"]["HTML"] == 5

    def test_submit_invalid_assessment(self, api_client, auth_headers):
        response = api_client.post("/api/assessments/submit", json={
            "assessment_id": 99999, "answers": [],
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_submit_requires_auth(self, api_client):
        response = api_client.post("/api/assessments/submit", json={
            "assessment_id": 1, "answers": [],
        })
        assert response.status_code == 401
