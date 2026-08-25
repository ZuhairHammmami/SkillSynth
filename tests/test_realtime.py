"""Realtime tests — SSE streams, public stats and its in-process cache."""

import pytest


class TestPublicStats:

    def test_public_stats_200(self, api_client):
        response = api_client.get("/api/public/stats")
        assert response.status_code == 200
        data = response.json()
        assert set(data) == {"users", "skills", "paths", "resources"}

    def test_public_stats_cached_identical(self, api_client):
        first = api_client.get("/api/public/stats")
        second = api_client.get("/api/public/stats")
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json() == second.json()


class TestSSE:

    def test_sse_token_issue(self, api_client, auth_headers):
        response = api_client.post("/api/auth/sse-token", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["expires_in"] == 300

    def test_events_stream_route_contract(self, api_client):
        """Verify the SSE endpoint is wired in the OpenAPI spec.

        Live streaming + content-type are exercised in the manual QA smoke
        (T8); the sync TestClient transport blocks on endless async
        generators, so the unit test asserts route registration only.
        """
        from backend.main import app
        spec = app.openapi()
        assert "/api/realtime/events" in spec["paths"]
        assert "get" in spec["paths"]["/api/realtime/events"]

    def test_events_stream_requires_token(self, api_client):
        response = api_client.get("/api/realtime/events")
        assert response.status_code == 401
