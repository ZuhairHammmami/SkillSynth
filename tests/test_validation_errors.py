"""422 validation responses must carry an array `detail` so per-field errors
can be rendered (admin fieldErrorsFrom / learner client)."""


def test_validation_error_returns_array_detail(api_client, admin_headers):
    response = api_client.post(
        "/api/admin/skills",
        headers=admin_headers,
        json={"name": "TmpBadSkill", "difficulty_level": 99},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    locs = [".".join(str(p) for p in d.get("loc", [])) for d in detail]
    assert any("difficulty_level" in loc for loc in locs)
