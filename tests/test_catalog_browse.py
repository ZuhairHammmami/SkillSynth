"""Learner catalog browse tests — skill detail (A), roles (B), per-skill
path generation (C).

These tests hit the shared session-scoped test DB (same veteran user as
test_learning.py), so every test cleans up the skills/paths it creates in a
finally block to keep count-based assertions order-independent.
"""

import uuid


def _fresh(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestCatalogSkillDetail:

    def test_get_skill_detail_shape(self, api_client, auth_headers):
        skills = api_client.get("/api/catalog/skills",
                                headers=auth_headers).json()["items"]
        assert skills
        skill_id = skills[0]["id"]
        response = api_client.get(f"/api/catalog/skills/{skill_id}",
                                  headers=auth_headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == skill_id
        assert {"prerequisites", "recommended", "category_name",
                "category_id", "name"} <= set(body)
        assert isinstance(body["prerequisites"], list)
        assert isinstance(body["recommended"], list)

    def test_get_skill_detail_missing_404(self, api_client, auth_headers):
        response = api_client.get("/api/catalog/skills/999999",
                                  headers=auth_headers)
        assert response.status_code == 404


class TestCatalogRoles:

    def test_list_roles_has_skills(self, api_client, auth_headers):
        response = api_client.get("/api/catalog/roles", headers=auth_headers)
        assert response.status_code == 200, response.text
        roles = response.json()
        assert isinstance(roles, list) and roles
        first = roles[0]
        assert {"id", "title", "description", "career_field", "skills"} <= set(first)
        assert isinstance(first["skills"], list)

    def test_catalog_requires_auth(self, api_client):
        assert api_client.get("/api/catalog/roles").status_code in (401, 403)


class TestGeneratePathForSkill:

    def _create_skill(self, api_client, admin_headers):
        response = api_client.post(
            "/api/admin/skills",
            json={"name": _fresh("CatalogSkill"), "difficulty_level": 3},
            headers=admin_headers)
        assert response.status_code == 200, response.text
        return response.json()

    def _cleanup(self, api_client, admin_headers, auth_headers, path_id, skill_id):
        if path_id is not None:
            api_client.delete(f"/api/paths/{path_id}", headers=auth_headers)
        if skill_id is not None:
            api_client.delete(f"/api/admin/skills/{skill_id}?force=true",
                              headers=admin_headers)

    def test_generate_path_creates_detail(self, api_client, admin_headers,
                                          auth_headers):
        skill = self._create_skill(api_client, admin_headers)
        path_id = None
        try:
            response = api_client.post(
                f"/api/generate-path/skill/{skill['id']}",
                json={"weekly_hours": 10}, headers=auth_headers)
            assert response.status_code == 200, response.text
            body = response.json()
            path_id = body["id"]
            assert body["id"]
            assert body["goal_job_role"] is None
            assert body["skills"]
            assert body["steps"]
        finally:
            self._cleanup(api_client, admin_headers, auth_headers,
                          path_id, skill["id"])

    def test_duplicate_guard_conflict(self, api_client, admin_headers,
                                      auth_headers):
        skill = self._create_skill(api_client, admin_headers)
        path_id = None
        try:
            first = api_client.post(f"/api/generate-path/skill/{skill['id']}",
                                    json={}, headers=auth_headers)
            assert first.status_code == 200, first.text
            path_id = first.json()["id"]
            second = api_client.post(f"/api/generate-path/skill/{skill['id']}",
                                     json={}, headers=auth_headers)
            assert second.status_code == 409, second.text
            assert "already" in second.json()["detail"]
        finally:
            self._cleanup(api_client, admin_headers, auth_headers,
                          path_id, skill["id"])

    def test_generate_path_missing_404(self, api_client, auth_headers):
        response = api_client.post("/api/generate-path/skill/999999",
                                   json={}, headers=auth_headers)
        assert response.status_code == 404
