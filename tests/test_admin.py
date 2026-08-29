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
        """Reads the full window (limit=200, the route max) so the
        breadth assertions stay stable as other tests append newer
        activity_log rows past the default 50-row page."""
        response = api_client.get("/api/admin/events",
                                  params={"limit": 200},
                                  headers=admin_headers)
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

    def test_list_assessments_shape(self, api_client, admin_headers):
        """Pins the /admin/assessments serializer (routers/evaluations_admin.py
        list_assessments): the legacy flat keys {id, skill_id, title,
        assessment_type, passing_score} plus the additive skill_name and
        question_count (Task 3)."""
        response = api_client.get("/api/admin/assessments",
                                  headers=admin_headers)
        assert response.status_code == 200
        assessments = response.json()
        assert isinstance(assessments, list) and assessments
        assert {
            "id", "skill_id", "title", "assessment_type",
            "passing_score", "skill_name", "question_count",
        } <= set(assessments[0])
        assert isinstance(assessments[0]["passing_score"], int)
        assert all(e["assessment_type"] == e["description"]
                   for e in assessments)
        assert all(e["question_count"] >= 0 for e in assessments)

    def test_post_backup_writes_into_cwd_backups_dir(
            self, api_client, admin_headers, tmp_path, monkeypatch):
        """POST /admin/backups copies the CWD-resolved skillsynth.db into
        ./backups/ (admin_service.backup_database); chdir'd to tmp_path with
        a stub db so neither the dev database nor the repo tree is written,
        then asserts success key + snapshot file + listing visibility."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "skillsynth.db").write_bytes(b"skillsynth-backup-stub")
        response = api_client.post("/api/admin/backups",
                                   headers=admin_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"] is True
        snapshot = tmp_path / data["path"]
        assert data["path"].startswith("backups")
        assert snapshot.exists() and snapshot.stat().st_size > 0
        listed = api_client.get("/api/admin/backups",
                                headers=admin_headers).json()
        assert any(entry["path"] == data["path"] for entry in listed)


class TestAdminUserUpdates:

    def test_put_user_happy_updates_profile_and_flag(
            self, api_client, admin_headers):
        email = _fresh_email("putme")
        user_id = api_client.post("/api/admin/users", json={
            "email": email, "password": "Zephyr#7781kq", "full_name": "Before",
        }, headers=admin_headers).json()["id"]
        response = api_client.put(f"/api/admin/users/{user_id}", json={
            "full_name": "After Name", "is_admin": True,
        }, headers=admin_headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["full_name"] == "After Name"
        assert body["is_admin"] is True
        api_client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)

    def test_put_user_password_reset_then_login(self, api_client, admin_headers):
        email = _fresh_email("pwswap")
        api_client.post("/api/admin/users", json={
            "email": email, "password": "Zephyr#7781kq",
        }, headers=admin_headers)
        users = api_client.get("/api/admin/users", headers=admin_headers).json()
        user_id = next(u for u in users if u["email"] == email)["id"]
        updated = api_client.put(f"/api/admin/users/{user_id}", json={
            "password": "Glimmer#Vex39qu",
        }, headers=admin_headers)
        assert updated.status_code == 200, updated.text
        login = api_client.post("/api/auth/token", data={
            "username": email, "password": "Glimmer#Vex39qu",
        })
        assert login.status_code == 200, login.text
        api_client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)

    def test_put_user_email_duplicate_conflict_409(
            self, api_client, admin_headers):
        email = _fresh_email("dupmail")
        user_id = api_client.post("/api/admin/users", json={
            "email": email, "password": "Zephyr#7781kq",
        }, headers=admin_headers).json()["id"]
        response = api_client.put(f"/api/admin/users/{user_id}", json={
            "email": "veteran@skillsynth.io",
        }, headers=admin_headers)
        assert response.status_code == 409
        api_client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)

    def test_put_user_email_duplicate_case_insensitive_409(
            self, api_client, admin_headers):
        email = _fresh_email("upcase")
        user_id = api_client.post("/api/admin/users", json={
            "email": email, "password": "Zephyr#7781kq",
        }, headers=admin_headers).json()["id"]
        response = api_client.put(f"/api/admin/users/{user_id}", json={
            "email": "VETERAN@SKILLSYNTH.IO",
        }, headers=admin_headers)
        assert response.status_code == 409
        api_client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)

    def test_put_user_not_found_404(self, api_client, admin_headers):
        response = api_client.put("/api/admin/users/999999",
                                  json={"full_name": "Ghost"},
                                  headers=admin_headers)
        assert response.status_code == 404

    def test_demote_self_guard_409(self, api_client, admin_headers):
        users = api_client.get("/api/admin/users", headers=admin_headers).json()
        admin = next(u for u in users if u["email"] == "admin@skillsynth.io")
        response = api_client.put(f"/api/admin/users/{admin['id']}",
                                  json={"is_admin": False},
                                  headers=admin_headers)
        assert response.status_code == 409
        still_admin = next(u for u in api_client.get(
            "/api/admin/users", headers=admin_headers).json()
            if u["id"] == admin["id"])
        assert still_admin["is_admin"] is True
