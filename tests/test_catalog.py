"""Catalog tests — skills/categories/resources listings, wizard options, admin CRUD."""

import uuid

import pytest


def _fresh(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestCatalogListings:

    def test_list_categories(self, api_client, admin_headers):
        response = api_client.get("/api/admin/categories", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 16

    def test_list_skills(self, api_client, admin_headers):
        response = api_client.get("/api/admin/skills", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 102
        assert {"id", "name", "category_id"} <= set(data[0])

    def test_list_resources(self, api_client, admin_headers):
        response = api_client.get("/api/admin/resources", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 87

    def test_wizard_options_structure(self, api_client):
        response = api_client.get("/api/wizard-options")
        assert response.status_code == 200
        data = response.json()
        assert set(data) == {"job_roles", "career_fields", "preferences"}
        assert isinstance(data["job_roles"], list)
        assert len(data["job_roles"]) == 25
        first = data["job_roles"][0]
        assert isinstance(first, dict)
        assert {"title", "career_field"} <= set(first)

    def test_wizard_options_job_roles_list_of_dicts(self, api_client):
        response = api_client.get("/api/wizard-options")
        data = response.json()
        assert all(isinstance(item, dict) for item in data["job_roles"])
        assert all("title" in item for item in data["job_roles"])


class TestAdminCatalogCrud:

    def test_create_and_delete_skill(self, api_client, admin_headers):
        name = _fresh("Skill")
        created = api_client.post("/api/admin/skills", json={"name": name},
                                  headers=admin_headers)
        assert created.status_code == 200, created.text
        skill_id = created.json()["id"]
        deleted = api_client.delete(f"/api/admin/skills/{skill_id}",
                                    headers=admin_headers)
        assert deleted.status_code == 200

    def test_create_skill_duplicate(self, api_client, admin_headers):
        response = api_client.post("/api/admin/skills", json={"name": "HTML"},
                                   headers=admin_headers)
        assert response.status_code == 400

    def test_create_and_delete_resource(self, api_client, admin_headers):
        title = _fresh("Resource")
        created = api_client.post("/api/admin/resources", json={
            "title": title, "url": "https://example.com/docs", "type": "article",
        }, headers=admin_headers)
        assert created.status_code == 200, created.text
        resource_id = created.json()["id"]
        deleted = api_client.delete(f"/api/admin/resources/{resource_id}",
                                    headers=admin_headers)
        assert deleted.status_code == 200

    def test_catalog_requires_admin(self, api_client, auth_headers):
        assert api_client.get("/api/admin/skills", headers=auth_headers).status_code == 403


class TestJobRoleListing:

    def test_get_job_roles_returns_serialized_list(self, api_client, admin_headers):
        response = api_client.get("/api/admin/job-roles", headers=admin_headers)
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list) and len(roles) >= 20
        assert {"id", "title", "description", "career_field", "skill_ids"} <= set(roles[0])
        assert isinstance(roles[0]["skill_ids"], list)


class TestCatalogPuts:

    def test_put_skill_happy(self, api_client, admin_headers):
        created = api_client.post("/api/admin/skills",
                                  json={"name": _fresh("Skill")},
                                  headers=admin_headers).json()
        new_name = _fresh("Renamed")
        response = api_client.put(f"/api/admin/skills/{created['id']}", json={
            "name": new_name, "description": "updated", "difficulty_level": 7,
        }, headers=admin_headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["name"] == new_name
        assert body["description"] == "updated"
        assert body["difficulty_level"] == 7
        api_client.delete(f"/api/admin/skills/{created['id']}",
                          headers=admin_headers)

    def test_put_resource_happy(self, api_client, admin_headers):
        created = api_client.post("/api/admin/resources", json={
            "title": _fresh("Res"), "url": "https://example.com/a",
            "type": "article",
        }, headers=admin_headers).json()
        response = api_client.put(f"/api/admin/resources/{created['id']}", json={
            "title": "Updated title", "is_free": False,
        }, headers=admin_headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["title"] == "Updated title"
        assert body["is_free"] is False
        api_client.delete(f"/api/admin/resources/{created['id']}",
                          headers=admin_headers)

    def test_put_category_happy(self, api_client, admin_headers):
        created = api_client.post("/api/admin/categories",
                                  json={"name": _fresh("Cat")},
                                  headers=admin_headers).json()
        new_name = _fresh("CatRenamed")
        response = api_client.put(f"/api/admin/categories/{created['id']}",
                                  json={"name": new_name},
                                  headers=admin_headers)
        assert response.status_code == 200, response.text
        assert response.json()["name"] == new_name
        api_client.delete(f"/api/admin/categories/{created['id']}",
                          headers=admin_headers)

    def test_put_job_role_happy_replaces_skill_ids(self, api_client, admin_headers):
        s1 = api_client.post("/api/admin/skills",
                             json={"name": _fresh("Skill")},
                             headers=admin_headers).json()["id"]
        created = api_client.post("/api/admin/job-roles",
                                  json={"title": _fresh("Role")},
                                  headers=admin_headers).json()
        new_title = _fresh("RoleRenamed")
        response = api_client.put(f"/api/admin/job-roles/{created['id']}", json={
            "title": new_title, "skill_ids": [s1],
        }, headers=admin_headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["title"] == new_title
        assert body["skill_ids"] == [s1]
        api_client.delete(f"/api/admin/job-roles/{created['id']}?force=true",
                          headers=admin_headers)
        api_client.delete(f"/api/admin/skills/{s1}", headers=admin_headers)


class TestCatalogPut404s:

    def test_put_skill_missing_404(self, api_client, admin_headers):
        response = api_client.put("/api/admin/skills/999999",
                                  json={"name": _fresh("Skill")},
                                  headers=admin_headers)
        assert response.status_code == 404

    def test_put_resource_missing_404(self, api_client, admin_headers):
        response = api_client.put("/api/admin/resources/999999",
                                  json={"title": "nope"},
                                  headers=admin_headers)
        assert response.status_code == 404

    def test_put_category_missing_404(self, api_client, admin_headers):
        response = api_client.put("/api/admin/categories/999999",
                                  json={"name": "nope"},
                                  headers=admin_headers)
        assert response.status_code == 404

    def test_put_job_role_missing_404(self, api_client, admin_headers):
        response = api_client.put("/api/admin/job-roles/999999",
                                  json={"title": "nope"},
                                  headers=admin_headers)
        assert response.status_code == 404

    def test_delete_skill_missing_404(self, api_client, admin_headers):
        response = api_client.delete("/api/admin/skills/999999",
                                     headers=admin_headers)
        assert response.status_code == 404
