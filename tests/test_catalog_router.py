"""Catalog router tests — learner browse API behind authentication."""

import pytest


class TestCategories:

    def test_list_categories(self, api_client, auth_headers):
        response = api_client.get("/api/catalog/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        assert all("id" in c and "name" in c and "skills" in c
                   for c in data["items"])

    def test_get_category(self, api_client, auth_headers):
        categories = api_client.get(
            "/api/catalog/categories", headers=auth_headers).json()["items"]
        response = api_client.get(
            f"/api/catalog/categories/{categories[0]['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_category_not_found(self, api_client, auth_headers):
        response = api_client.get(
            "/api/catalog/categories/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_categories_requires_auth(self, api_client):
        assert api_client.get("/api/catalog/categories").status_code == 401


class TestSkills:

    def test_list_skills(self, api_client, auth_headers):
        response = api_client.get("/api/catalog/skills", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

    def test_skills_requires_auth(self, api_client):
        assert api_client.get("/api/catalog/skills").status_code == 401
