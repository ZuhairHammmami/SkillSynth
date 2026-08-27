"""Analytics tests — learner dashboard, skill growth, path progress, history."""

import pytest


class TestDashboard:

    def test_dashboard_keys(self, api_client, auth_headers):
        response = api_client.get("/api/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) >= {
            "total_paths", "total_completed_steps", "completed_steps",
            "total_steps", "completion_rate", "mastered_skills",
            "learning_skills", "total_skill_areas", "weekly_completions",
            "total_hours", "completed_hours", "remaining_hours",
            "learning_velocity", "recent_activity", "path_progress",
        }

    def test_dashboard_values(self, api_client, auth_headers):
        data = api_client.get("/api/analytics/dashboard",
                              headers=auth_headers).json()
        assert data["total_paths"] == 2
        assert data["completed_steps"] == 7
        assert data["total_steps"] == 17
        assert isinstance(data["recent_activity"], list)
        assert isinstance(data["path_progress"], list)

    def test_dashboard_requires_auth(self, api_client):
        assert api_client.get("/api/analytics/dashboard").status_code == 401


class TestSkillGrowth:

    def test_skill_growth(self, api_client, auth_headers):
        response = api_client.get("/api/analytics/skill-growth", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) >= {
            "skills", "mastered_count", "in_progress_count",
            "not_started_count", "weak_skills", "strong_skills",
            "knowledge_gaps",
        }
        assert isinstance(data["skills"], list)
        assert all(set(s) == {"skill", "level", "status"} for s in data["skills"])

    def test_skill_growth_requires_auth(self, api_client):
        assert api_client.get("/api/analytics/skill-growth").status_code == 401


class TestPathProgressAndHistory:

    def test_path_progress(self, api_client, auth_headers):
        paths = api_client.get("/api/paths/", headers=auth_headers).json()
        response = api_client.get(f"/api/analytics/path-progress/{paths[0]['id']}",
                                  headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) >= {
            "path_id", "total_steps", "completed_steps",
            "completion_percentage", "step_progress",
        }

    def test_path_progress_not_found(self, api_client, auth_headers):
        assert api_client.get("/api/analytics/path-progress/99999",
                              headers=auth_headers).status_code == 404

    def test_learning_history(self, api_client, auth_headers):
        response = api_client.get("/api/analytics/learning-history",
                                  headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert set(data) >= {
            "recent_activity", "total_completions", "weekly_completions",
            "daily_activity",
        }
        assert data["total_completions"] == 7


class TestProgressByCategory:

    def test_progress_by_category(self, api_client, auth_headers):
        response = api_client.get("/api/analytics/progress-by-category",
                                  headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)

    def test_progress_by_category_requires_auth(self, api_client):
        assert api_client.get(
            "/api/analytics/progress-by-category").status_code == 401
