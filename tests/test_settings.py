"""tests/test_settings.py — file-backed settings + admin feature-flags toggle."""

import json
from datetime import datetime, timezone

import pytest
from jose import jwt as jose_jwt

from backend.dto.auth import PasswordValidator
from backend.limiter import limiter
from backend.services import auth_service, settings_service

RO_ONLY_KEYS = ("app_mode", "ai_path_generation", "csrf_protection")


@pytest.fixture(autouse=True)
def _reset_cache():
    """Clear the in-memory settings cache after each test so later
    suites reseed from the (possibly reverted) SETTINGS_PATH."""
    yield
    settings_service._CACHE.clear()


def _read_file(path):
    """Load the JSON settings file at path for persistence assertions."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_set_and_persist(tmp_path, monkeypatch):
    """set_ai_enabled writes through to disk and is read back as True."""
    monkeypatch.setattr(settings_service, "SETTINGS_PATH",
                        str(tmp_path / "settings.json"))
    settings_service._CACHE.clear()
    settings_service.set_ai_enabled(True)
    assert settings_service.is_ai_enabled() is True
    assert _read_file(settings_service.SETTINGS_PATH)["ai_enabled"] is True


def test_seeded_from_env(tmp_path, monkeypatch):
    """First access seeds ai_enabled from the AI_ENABLED env var."""
    monkeypatch.setattr(settings_service, "SETTINGS_PATH",
                        str(tmp_path / "settings.json"))
    monkeypatch.setenv("AI_ENABLED", "true")
    settings_service._CACHE.clear()
    assert settings_service.is_ai_enabled() is True
    assert _read_file(settings_service.SETTINGS_PATH)["ai_enabled"] is True


def test_seeded_false_from_env(tmp_path, monkeypatch):
    """Missing file with AI_ENABLED=false yields a disabled default."""
    monkeypatch.setattr(settings_service, "SETTINGS_PATH",
                        str(tmp_path / "settings.json"))
    monkeypatch.setenv("AI_ENABLED", "false")
    settings_service._CACHE.clear()
    assert settings_service.is_ai_enabled() is False


def test_admin_feature_flags_toggle(api_client, admin_headers, tmp_path,
                                    monkeypatch):
    """Admin can read and PUT the AI toggle; runtime state flips accordingly."""
    monkeypatch.setattr(settings_service, "SETTINGS_PATH",
                        str(tmp_path / "settings.json"))
    settings_service._CACHE.clear()

    get = api_client.get("/api/admin/feature-flags", headers=admin_headers)
    assert get.status_code == 200
    assert "ai_enabled" in get.json()

    put = api_client.put("/api/admin/feature-flags",
                         json={"ai_enabled": True},
                         headers=admin_headers)
    assert put.status_code == 200
    assert put.json()["ai_enabled"] is True
    assert settings_service.is_ai_enabled() is True


def test_feature_flags_rejects_non_admin(api_client, auth_headers, tmp_path,
                                         monkeypatch):
    """A non-admin bearer token cannot mutate the AI toggle (403)."""
    monkeypatch.setattr(settings_service, "SETTINGS_PATH",
                        str(tmp_path / "settings.json"))
    settings_service._CACHE.clear()
    resp = api_client.put("/api/admin/feature-flags",
                          json={"ai_enabled": True},
                          headers=auth_headers)
    assert resp.status_code == 403


def _use_temp_settings(tmp_path, monkeypatch):
    """Point settings_service at an isolated temp file and clear its cache."""
    monkeypatch.setattr(settings_service, "SETTINGS_PATH",
                        str(tmp_path / "settings.json"))
    settings_service._CACHE.clear()


def test_feature_flags_schema_shape(api_client, admin_headers, tmp_path,
                                    monkeypatch):
    """Schema returns 13 keys, each with type/editable/live/default, and the
    read-only keys are flagged (editable False)."""
    _use_temp_settings(tmp_path, monkeypatch)
    resp = api_client.get("/api/admin/feature-flags/schema",
                          headers=admin_headers)
    assert resp.status_code == 200
    schema = resp.json()
    assert len(schema) == 13
    for key, meta in schema.items():
        assert {"type", "editable", "live", "default"} <= set(meta), key
    for key in RO_ONLY_KEYS:
        assert schema[key]["editable"] is False
    assert any(m["editable"] for m in schema.values())


@pytest.mark.parametrize("payload", [
    {"unknown_key": 1},
    {"app_mode": "prod"},
    {"ai_path_generation": False},
    {"csrf_protection": False},
    {"session_timeout_hours": True},
    {"session_timeout_hours": 1000},
    {"cors_origins": ["ftp://x"]},
])
def test_feature_flags_put_schema_422(api_client, admin_headers, tmp_path,
                                      monkeypatch, payload):
    """Unknown, read-only, wrong-type and out-of-range flags all 422."""
    _use_temp_settings(tmp_path, monkeypatch)
    resp = api_client.put("/api/admin/feature-flags", json=payload,
                          headers=admin_headers)
    assert resp.status_code == 422, f"{payload} -> {resp.status_code}"


def test_feature_flags_bulk_put_happy_path(api_client, admin_headers,
                                           tmp_path, monkeypatch):
    """Bulk PUT persists live flags; GET reflects and store contains them."""
    _use_temp_settings(tmp_path, monkeypatch)
    body = {"registration_enabled": False, "session_timeout_hours": 12,
            "account_lockout_attempts": 3, "lockout_minutes": 5}
    resp = api_client.put("/api/admin/feature-flags", json=body,
                          headers=admin_headers)
    assert resp.status_code == 200, resp.text
    returned = resp.json()
    assert returned["registration_enabled"] is False
    assert returned["session_timeout_hours"] == 12
    assert returned["account_lockout_attempts"] == 3
    flags = api_client.get("/api/admin/feature-flags",
                           headers=admin_headers).json()
    assert flags["registration_enabled"] is False
    assert flags["session_timeout_hours"] == 12
    assert flags["lockout_minutes"] == 5
    stored = settings_service.get_all()
    assert stored["registration_enabled"] is False
    assert stored["session_timeout_hours"] == 12


def test_register_disabled_when_flag_false(api_client, admin_headers,
                                           tmp_path, monkeypatch):
    """registration_enabled=false makes /auth/register return 403."""
    _use_temp_settings(tmp_path, monkeypatch)
    put = api_client.put("/api/admin/feature-flags",
                         json={"registration_enabled": False},
                         headers=admin_headers)
    assert put.status_code == 200
    resp = api_client.post("/api/auth/register", json={
        "email": "blocked@test.io", "password": "Zephyr#7781kq",
        "full_name": "Blocked"})
    assert resp.status_code == 403


def test_live_password_policy_min_length(api_client, admin_headers,
                                         tmp_path, monkeypatch):
    """Raising password_policy.min_length rejects a shorter valid-looking pw."""
    _use_temp_settings(tmp_path, monkeypatch)
    put = api_client.put("/api/admin/feature-flags",
                         json={"password_policy": {"min_length": 9}},
                         headers=admin_headers)
    assert put.status_code == 200
    reg = api_client.post("/api/auth/register", json={
        "email": "pol9@test.io", "password": "Ab1@efgh", "full_name": "Pol"})
    assert reg.status_code == 422
    reg_ok = api_client.post("/api/auth/register", json={
        "email": "pol10@test.io", "password": "Ab1@efghi", "full_name": "Pol"})
    assert reg_ok.status_code == 200


def test_limiter_enabled_flips_with_flag(api_client, admin_headers,
                                         tmp_path, monkeypatch):
    """rate_limiting=false sets limiter.enabled False; true restores it."""
    _use_temp_settings(tmp_path, monkeypatch)
    limiter.enabled = False
    try:
        put_off = api_client.put("/api/admin/feature-flags",
                                 json={"rate_limiting": False},
                                 headers=admin_headers)
        assert put_off.status_code == 200
        assert limiter.enabled is False
        put_on = api_client.put("/api/admin/feature-flags",
                                json={"rate_limiting": True},
                                headers=admin_headers)
        assert put_on.status_code == 200
        assert limiter.enabled is True
    finally:
        limiter.enabled = False


def test_lockout_from_settings(api_client, admin_headers, tmp_path,
                               monkeypatch):
    """account_lockout_attempts=3 blocks the 4th (correct) login."""
    _use_temp_settings(tmp_path, monkeypatch)
    email = "lockout@test.io"
    password = "Zephyr#7781kq"
    put = api_client.put("/api/admin/feature-flags",
                         json={"account_lockout_attempts": 3},
                         headers=admin_headers)
    assert put.status_code == 200
    reg = api_client.post("/api/auth/register", json={
        "email": email, "password": password, "full_name": "Locked"})
    assert reg.status_code == 200, reg.text
    for _ in range(3):
        bad = api_client.post("/api/auth/token",
                              data={"username": email, "password": "wrongpw1"})
        assert bad.status_code == 401
    good = api_client.post("/api/auth/token",
                           data={"username": email, "password": password})
    assert good.status_code == 429


def test_session_timeout_exp_honors_flag(tmp_path, monkeypatch):
    """create_access_token expiry honors the live session_timeout_hours flag."""
    _use_temp_settings(tmp_path, monkeypatch)
    settings_service.set_setting("session_timeout_hours", 1)
    token = auth_service.create_access_token({"sub": "x@y.io"})
    payload = jose_jwt.decode(token, auth_service.SECRET_KEY,
                              algorithms=["HS256"],
                              options={"verify_exp": False})
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    minutes = (exp - datetime.now(timezone.utc)).total_seconds() / 60
    assert 55 <= minutes <= 61


def test_password_validator_live_policy(tmp_path, monkeypatch):
    """PasswordValidator reads the live min_length; direct, no HTTP."""
    _use_temp_settings(tmp_path, monkeypatch)
    settings_service.set_setting("password_policy", {"min_length": 9})
    with pytest.raises(ValueError):
        PasswordValidator.validate("Ab1@efgh")
    PasswordValidator.validate("Ab1@efghi")
