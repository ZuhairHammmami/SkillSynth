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
