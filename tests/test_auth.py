"""Auth flow tests — register, login, profile, password lifecycle, csrf/sse."""

import uuid

import pytest

from tests.integrity_support import PASSWORD


def _fresh_email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.com"


class TestAuth:

    def test_register(self, api_client):
        email = _fresh_email("user")
        response = api_client.post("/api/auth/register", json={
            "email": email, "password": "TestPass@123", "full_name": "Test User",
        })
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == email
        assert data["full_name"] == "Test User"
        assert data["is_admin"] is False

    def test_register_duplicate(self, api_client):
        response = api_client.post("/api/auth/register", json={
            "email": "veteran@skillsynth.io", "password": "TestPass@123",
            "full_name": "Duplicate",
        })
        assert response.status_code == 400

    def test_register_weak_password(self, api_client):
        response = api_client.post("/api/auth/register", json={
            "email": _fresh_email("weak"), "password": "short",
        })
        assert response.status_code == 422

    def test_login_success(self, api_client):
        response = api_client.post("/api/auth/token", data={
            "username": "veteran@skillsynth.io", "password": "Veteran@123456",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["access_token"]

    def test_login_wrong_password(self, api_client):
        response = api_client.post("/api/auth/token", data={
            "username": "veteran@skillsynth.io", "password": "wrongpass",
        })
        assert response.status_code == 401

    def test_login_wrong_email(self, api_client):
        response = api_client.post("/api/auth/token", data={
            "username": "nobody@nowhere.com", "password": "SomePass@123",
        })
        assert response.status_code == 401

    def test_me_flat_fields(self, api_client, auth_headers):
        response = api_client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "veteran@skillsynth.io"
        assert data["is_admin"] is False
        assert set(data) == {
            "id", "email", "full_name", "is_admin", "skill_profile",
            "created_at", "updated_at",
        }
        assert isinstance(data["skill_profile"], dict)

    def test_me_unauthorized(self, api_client):
        assert api_client.get("/api/auth/me").status_code == 401

    def test_update_profile(self, api_client, auth_headers):
        response = api_client.put("/api/auth/me", json={
            "full_name": "Updated Veteran",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Veteran"

    def test_change_password(self, api_client):
        email = _fresh_email("chpw")
        api_client.post("/api/auth/register", json={
            "email": email, "password": "OldPass@123",
        })
        login = api_client.post("/api/auth/token", data={
            "username": email, "password": "OldPass@123",
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.post("/api/auth/change-password", json={
            "current_password": "OldPass@123", "new_password": "NewPass@456",
        }, headers=headers)
        assert response.status_code == 200
        relogin = api_client.post("/api/auth/token", data={
            "username": email, "password": "NewPass@456",
        })
        assert relogin.status_code == 200

    def test_change_password_wrong_current(self, api_client, auth_headers):
        response = api_client.post("/api/auth/change-password", json={
            "current_password": "wrongpassword", "new_password": "NewPass@456",
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_forgot_password(self, api_client):
        response = api_client.post("/api/auth/forgot-password", json={
            "email": "veteran@skillsynth.io",
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "reset_token" in data

    def test_forgot_password_nonexistent(self, api_client):
        response = api_client.post("/api/auth/forgot-password", json={
            "email": "nobody@nowhere.com",
        })
        assert response.status_code == 200
        assert "reset_token" not in response.json()

    def test_reset_password(self, api_client):
        email = _fresh_email("reset")
        api_client.post("/api/auth/register", json={
            "email": email, "password": "OldPass@123",
        })
        forgot = api_client.post("/api/auth/forgot-password", json={"email": email})
        token = forgot.json()["reset_token"]
        response = api_client.post("/api/auth/reset-password", json={
            "token": token, "new_password": "Reset@789",
        })
        assert response.status_code == 200
        relogin = api_client.post("/api/auth/token", data={
            "username": email, "password": "Reset@789",
        })
        assert relogin.status_code == 200

    def test_sse_token(self, api_client, auth_headers):
        response = api_client.post("/api/auth/sse-token", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["expires_in"] == 300
        assert data["token"]

    def test_csrf_token(self, api_client):
        response = api_client.get("/api/auth/csrf")
        assert response.status_code == 200
        assert "csrf_token" in response.json()


class TestAccountLockout:
    """Pins the implemented lockout semantics of services/auth_service.py
    (MAX_LOGIN_ATTEMPTS=5, LOGIN_LOCKOUT_MINUTES=15, in-memory per-email
    window): failures #1-#5 each still answer 401 — the 5th trips the
    lock — then every further attempt inside the window maps to 429 via
    routers/auth.py's "Account locked" prefix check, correct password
    included, because authenticate() gates on check_login_allowed() before
    verifying credentials. Uses a throwaway account so the shared
    _login_attempts state never touches seeded logins."""

    def test_lock_after_five_failures_then_429_even_with_correct_password(
            self, api_client):
        email = f"lockout_{uuid.uuid4().hex[:8]}@test.com"
        created = api_client.post("/api/auth/register", json={
            "email": email, "password": PASSWORD})
        assert created.status_code == 200, created.text
        for _ in range(5):
            failed = api_client.post("/api/auth/token", data={
                "username": email, "password": "TotallyWrong#999x"})
            assert failed.status_code == 401
        locked = api_client.post("/api/auth/token", data={
            "username": email, "password": PASSWORD})
        assert locked.status_code == 429, locked.text
        assert locked.json()["detail"].startswith("Account locked")
        still_locked = api_client.post("/api/auth/token", data={
            "username": email, "password": "TotallyWrong#999x"})
        assert still_locked.status_code == 429
