"""DTO validation tests — ensures all admin CRUD DTOs reject invalid input with 422.

Covers SkillCreate/SkillUpdate, CategoryCreate, ResourceCreate/ResourceUpdate,
JobRoleCreate/JobRoleUpdate, AdminCreateUser/AdminUserUpdate, AssessmentCreate
and QuestionCreate per Task 5. Free-text fields are sanitized; length/range/
format/positive-id rules surface as 422 (Pydantic validation errors) — the
array `detail` shape is pinned in tests/test_validation_errors.py.
"""

import uuid


def _fresh(prefix):
    """Return a unique-friendly string for admin CRUD names/titles."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestSkillDtoValidation:
    """SkillCreate/SkillUpdate validation rules."""

    def test_skill_name_required(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills", json={}, headers=admin_headers)
        assert r.status_code == 422

    def test_skill_name_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": "x" * 101}, headers=admin_headers)
        assert r.status_code == 422

    def test_skill_name_markup_stripped(self, api_client, admin_headers):
        name = _fresh("SafeSkill")
        r = api_client.post("/api/admin/skills",
                            json={"name": f"<b>{name}</b>"}, headers=admin_headers)
        assert r.status_code == 200
        assert "<" not in r.json()["name"]
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_description_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "description": "x" * 2001},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_description_sanitized(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "description": "<script>alert(1)</script>ok"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<script>" not in r.json()["description"]
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_difficulty_level_range(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "difficulty_level": 0},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_difficulty_level_over_max(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "difficulty_level": 6},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_color_invalid_hex(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "color": "not-a-color"},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_color_valid_hex(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "color": "#ff00aa"},
                            headers=admin_headers)
        assert r.status_code == 200
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_color_3_digit_hex(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "color": "#abc"},
                            headers=admin_headers)
        assert r.status_code == 200
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_icon_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "icon": "x" * 101},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_icon_sanitized(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "icon": "<img onerror=alert(1)>"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<" not in r.json()["icon"]
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_estimated_hours_negative(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "estimated_hours": -1},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_prerequisite_ids_must_be_positive(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "prerequisite_ids": [0]},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_update_color_invalid(self, api_client, admin_headers):
        created = api_client.post("/api/admin/skills",
                                  json={"name": _fresh("S")},
                                  headers=admin_headers).json()
        r = api_client.put(f"/api/admin/skills/{created['id']}",
                           json={"color": "bad"}, headers=admin_headers)
        assert r.status_code == 422
        api_client.delete(f"/api/admin/skills/{created['id']}", headers=admin_headers)

    def test_skill_update_description_sanitized(self, api_client, admin_headers):
        created = api_client.post("/api/admin/skills",
                                  json={"name": _fresh("S")},
                                  headers=admin_headers).json()
        r = api_client.put(f"/api/admin/skills/{created['id']}",
                           json={"description": "<b>bold</b> text"},
                           headers=admin_headers)
        assert r.status_code == 200
        assert "<b>" not in r.json()["description"]
        api_client.delete(f"/api/admin/skills/{created['id']}", headers=admin_headers)


class TestCategoryDtoValidation:
    def test_category_description_sanitized(self, api_client, admin_headers):
        name = _fresh("Cat")
        r = api_client.post("/api/admin/categories",
                            json={"name": name, "description": "<script>x</script>"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<script>" not in r.json()["description"]
        api_client.delete(f"/api/admin/categories/{r.json()['id']}", headers=admin_headers)


class TestResourceDtoValidation:
    def test_resource_update_title_sanitized(self, api_client, admin_headers):
        created = api_client.post("/api/admin/resources", json={
            "title": _fresh("R"), "url": "https://example.com", "type": "article",
        }, headers=admin_headers).json()
        r = api_client.put(f"/api/admin/resources/{created['id']}",
                           json={"title": "<img onerror=alert(1)>"},
                           headers=admin_headers)
        assert r.status_code == 200
        assert "<" not in r.json()["title"]
        api_client.delete(f"/api/admin/resources/{created['id']}", headers=admin_headers)

    def test_resource_update_url_invalid_scheme(self, api_client, admin_headers):
        created = api_client.post("/api/admin/resources", json={
            "title": _fresh("R"), "url": "https://example.com", "type": "article",
        }, headers=admin_headers).json()
        r = api_client.put(f"/api/admin/resources/{created['id']}",
                           json={"url": "javascript:alert(1)"},
                           headers=admin_headers)
        assert r.status_code == 422
        api_client.delete(f"/api/admin/resources/{created['id']}", headers=admin_headers)

    def test_resource_type_sanitized_lowercase(self, api_client, admin_headers):
        name = _fresh("R")
        r = api_client.post("/api/admin/resources", json={
            "title": name, "url": "https://example.com", "type": "ARTICLE",
        }, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["type"] == "article"
        api_client.delete(f"/api/admin/resources/{r.json()['id']}", headers=admin_headers)


class TestJobRoleDtoValidation:
    def test_job_role_description_sanitized(self, api_client, admin_headers):
        title = _fresh("Role")
        r = api_client.post("/api/admin/job-roles",
                            json={"title": title, "description": "<b>bold</b>"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<b>" not in r.json()["description"]
        api_client.delete(f"/api/admin/job-roles/{r.json()['id']}?force=true",
                          headers=admin_headers)

    def test_job_role_update_skill_ids_must_be_positive(self, api_client, admin_headers):
        created = api_client.post("/api/admin/job-roles",
                                  json={"title": _fresh("Role")},
                                  headers=admin_headers).json()
        r = api_client.put(f"/api/admin/job-roles/{created['id']}",
                           json={"skill_ids": [0]},
                           headers=admin_headers)
        assert r.status_code == 422
        api_client.delete(f"/api/admin/job-roles/{created['id']}?force=true",
                          headers=admin_headers)


class TestAdminUserDtoValidation:
    def test_admin_user_full_name_sanitized(self, api_client, admin_headers):
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        r = api_client.post("/api/admin/users", json={
            "email": email, "password": "Strong@123",
            "full_name": "<script>alert(1)</script>",
        }, headers=admin_headers)
        assert r.status_code == 200
        assert "<script>" not in r.json()["full_name"]
        api_client.delete(f"/api/admin/users/{r.json()['id']}", headers=admin_headers)

    def test_admin_user_update_full_name_sanitized(self, api_client, admin_headers):
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        created = api_client.post("/api/admin/users", json={
            "email": email, "password": "Strong@123",
        }, headers=admin_headers).json()
        r = api_client.put(f"/api/admin/users/{created['id']}",
                           json={"full_name": "<b>X</b>"},
                           headers=admin_headers)
        assert r.status_code == 200
        assert "<b>" not in r.json()["full_name"]
        api_client.delete(f"/api/admin/users/{created['id']}", headers=admin_headers)


class TestQuestionDtoValidation:
    def test_question_options_empty_string_rejected(self, api_client, admin_headers):
        # Create assessment first
        r = api_client.post("/api/admin/assessments", json={
            "title": _fresh("Assess"), "skill_id": None,
        }, headers=admin_headers)
        assert r.status_code == 200
        aid = r.json()["id"]
        qr = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q?", "options": ["", "B"], "correct_index": 1,
        }, headers=admin_headers)
        assert qr.status_code == 422
        api_client.delete(f"/api/admin/assessments/{aid}", headers=admin_headers)

    def test_question_options_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/assessments", json={
            "title": _fresh("Assess"), "skill_id": None,
        }, headers=admin_headers)
        aid = r.json()["id"]
        qr = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q?", "options": ["x" * 501, "B"], "correct_index": 1,
        }, headers=admin_headers)
        assert qr.status_code == 422
        api_client.delete(f"/api/admin/assessments/{aid}", headers=admin_headers)

    def test_question_options_sanitized(self, api_client, admin_headers):
        r = api_client.post("/api/admin/assessments", json={
            "title": _fresh("Assess"), "skill_id": None,
        }, headers=admin_headers)
        aid = r.json()["id"]
        qr = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q?",
            "options": ["<b>bold</b>", "plain"],
            "correct_index": 0,
        }, headers=admin_headers)
        assert qr.status_code == 200
        assert "<b>" not in qr.json()["options"][0]
        # Assessment now holds a question, so a restricted delete would 409;
        # force=true keeps the shared session DB clean.
        api_client.delete(f"/api/admin/assessments/{aid}?force=true",
                          headers=admin_headers)
