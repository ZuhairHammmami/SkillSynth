"""Tests for pagination of list endpoints."""
import pytest
from tests.conftest import client


class TestCatalogSkillsPagination:
    """GET /api/catalog/skills pagination."""

    def test_page1_returns_envelope(self, auth_headers):
        resp = client.get("/api/catalog/skills?page=1&page_size=5", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "pages" in data
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["items"]) <= 5

    def test_page2_returns_different_items(self, auth_headers):
        resp1 = client.get("/api/catalog/skills?page=1&page_size=5", headers=auth_headers)
        resp2 = client.get("/api/catalog/skills?page=2&page_size=5", headers=auth_headers)
        assert resp1.status_code == 200 and resp2.status_code == 200
        ids1 = [s["id"] for s in resp1.json()["items"]]
        ids2 = [s["id"] for s in resp2.json()["items"]]
        assert ids1 != ids2
        assert set(ids1).isdisjoint(set(ids2))

    def test_default_returns_envelope(self, auth_headers):
        resp_all = client.get("/api/catalog/skills", headers=auth_headers)
        assert resp_all.status_code == 200
        data = resp_all.json()
        assert "items" in data and "total" in data
        assert data["page"] == 1 and data["page_size"] == 50
        assert len(data["items"]) <= 50


class TestCatalogCategoriesPagination:
    """GET /api/catalog/categories pagination."""

    def test_returns_envelope(self, auth_headers):
        resp = client.get("/api/catalog/categories?page=1&page_size=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))


class TestAdminEndpointsPagination:
    """GET /api/admin/{users,skills,categories,job-roles} pagination."""

    def test_admin_users_envelope(self, admin_headers):
        resp = client.get("/api/admin/users?page=1&page_size=5", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))

    def test_admin_skills_envelope(self, admin_headers):
        resp = client.get("/api/admin/skills?page=1&page_size=5", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))

    def test_admin_categories_envelope(self, admin_headers):
        resp = client.get("/api/admin/categories?page=1&page_size=5", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))

    def test_admin_job_roles_envelope(self, admin_headers):
        resp = client.get("/api/admin/job-roles?page=1&page_size=5", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))


class TestPathsPagination:
    """GET /api/paths/ pagination."""

    def test_returns_envelope(self, auth_headers):
        resp = client.get("/api/paths/?page=1&page_size=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))


class TestAnalyticsSkillGrowthPagination:
    """GET /api/analytics/skill-growth pagination."""

    def test_returns_envelope(self, auth_headers):
        resp = client.get("/api/analytics/skill-growth?page=1&page_size=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(k in data for k in ("items", "total", "page", "page_size", "pages"))
