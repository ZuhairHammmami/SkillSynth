"""Admin tests — user CRUD, privilege gate, reports, activity feed, system ops."""

import uuid

import pytest


def _fresh_email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.com"


class TestAdminGate:

    def test_non_admin_403(self, api_client, auth_headers):
        assert api_client.get("/api/admin/users", headers=auth_headers).status_code == 403

    def test_admin_401_without_token(self, api_client):
        assert api_client.get("/api/admin/users").status_code == 401


class TestAdminUsers:

    def test_list_users(self, api_client, admin_headers):
        response = api_client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 5
        assert {"id", "email", "is_admin"} <= set(users[0])

    def test_create_and_delete_user(self, api_client, admin_headers):
        email = _fresh_email("adminmade")
        created = api_client.post("/api/admin/users", json={
            "email": email, "password": "Zephyr#7781kq", "full_name": "Admin Made",
            "is_admin": False,
        }, headers=admin_headers)
        assert created.status_code == 200, created.text
        user_id = created.json()["id"]
        deleted = api_client.delete(f"/api/admin/users/{user_id}",
                                    headers=admin_headers)
        assert deleted.status_code == 200

    def test_create_user_duplicate(self, api_client, admin_headers):
        response = api_client.post("/api/admin/users", json={
            "email": "veteran@skillsynth.io", "password": "SomePass@123",
        }, headers=admin_headers)
        assert response.status_code == 400

    def test_delete_self_guard(self, api_client, admin_headers):
        users = api_client.get("/api/admin/users", headers=admin_headers).json()
        admin = next(u for u in users if u["email"] == "admin@skillsynth.io")
        response = api_client.delete(f"/api/admin/users/{admin['id']}",
                                     headers=admin_headers)
        assert response.status_code == 400


class TestAdminReports:

    def test_aggregated_report(self, api_client, admin_headers):
        response = api_client.get("/api/admin/reports/aggregated",
                                  headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) >= {
            "user_activity", "content_engagement", "system_health",
            "most_active_users", "most_requested_skills", "total_hours_learned",
            "average_completion_rate", "total_assessment_attempts",
            "average_assessment_score",
        }
        assert set(data["user_activity"]) >= {
            "total_users", "new_users_last_24h", "new_users_last_7d",
            "users_with_paths",
        }
        assert set(data["system_health"]) >= {
            "database_status", "total_users", "total_paths", "total_assessments",
        }

    def test_system_health(self, api_client, admin_headers):
        response = api_client.get("/api/admin/reports/system-health",
                                  headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["database_status"] == "Connected"
        assert data["total_users"] >= 5

    def test_admin_list_paths(self, api_client, admin_headers):
        response = api_client.get("/api/admin/paths", headers=admin_headers)
        assert response.status_code == 200
        paths = response.json()
        assert isinstance(paths, list)
        assert len(paths) >= 5


class TestAdminActivity:

    def test_events_feed(self, api_client, admin_headers):
        response = api_client.get("/api/admin/events", headers=admin_headers)
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
        assert events
        categories = {e["category"] for e in events}
        assert {"audit", "auth", "system", "learning"} <= categories
        assert any(e["action"] == "password_reset_requested" for e in events)

    def test_events_filter_category(self, api_client, admin_headers):
        response = api_client.get("/api/admin/events", params={"category": "auth"},
                                  headers=admin_headers)
        assert response.status_code == 200
        assert all(e["category"] == "auth" for e in response.json())


class TestAdminSystem:

    def test_feature_flags(self, api_client, admin_headers):
        response = api_client.get("/api/admin/feature-flags", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) >= {
            "app_mode", "registration_enabled", "ai_path_generation",
            "real_time_updates", "csrf_protection", "rate_limiting",
            "password_policy", "session_timeout_hours",
            "account_lockout_attempts", "lockout_minutes", "cors_origins",
        }

    def test_db_inspector(self, api_client, admin_headers):
        response = api_client.get("/api/admin/db-inspector", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_tables"] == 15
        assert data["integrity_check"] is True
        assert isinstance(data["tables"], list)

    def test_backups(self, api_client, admin_headers):
        response = api_client.get("/api/admin/backups", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
