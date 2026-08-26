"""CORS policy tests — dev origins allow-listed, strangers rejected.

Pins the contract browsers depend on: preflight (OPTIONS + Origin +
Access-Control-Request-Method) must answer 200 with access-control-
allow-origin echoed for every configured dev origin and WITHOUT the
header for unconfigured ones. Runs against the real middleware stack
(CORSMiddleware answers before routing; no DB involved).
"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

DEV_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]


def _preflight(origin):
    """OPTIONS preflight probe returning (status, acao-header-or-None)."""
    response = client.options(
        "/api/auth/token",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    return response.status_code, response.headers.get("access-control-allow-origin")


def test_preflight_allowed_for_every_dev_origin():
    """Each configured dev origin gets 200 + its own ACAO echo."""
    for origin in DEV_ORIGINS:
        status, acao = _preflight(origin)
        assert status == 200, f"preflight failed for {origin}"
        assert acao == origin, f"missing/mismatched ACAO for {origin}"


def test_preflight_rejected_for_unknown_origin():
    """An unconfigured origin gets 400 with NO ACAO header (Starlette
    CORSMiddleware semantics for disallowed preflights)."""
    status, acao = _preflight("https://evil.example.com")
    assert status == 400
    assert acao is None


def test_actual_request_echoes_origin():
    """A simple GET carries ACAO so non-preflight responses are readable."""
    response = client.get(
        "/api/public/stats", headers={"Origin": "http://localhost:3001"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == \
        "http://localhost:3001"
