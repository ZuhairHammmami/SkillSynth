"""Catalog integrity tests — FK validation, cycles, rename dups,
restricted deletes, force deletes and the IntegrityError safety net."""

import uuid


def _fresh(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _mk_skill(api_client, headers, name=None):
    """Create a throwaway skill and return its id."""
    response = api_client.post("/api/admin/skills",
                               json={"name": name or _fresh("Skill")},
                               headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["id"]


class TestRenameDuplicates:

    def test_put_skill_rename_duplicate_409(self, api_client, admin_headers):
        skill_id = _mk_skill(api_client, admin_headers)
        response = api_client.put(f"/api/admin/skills/{skill_id}",
                                  json={"name": "HTML"},
                                  headers=admin_headers)
        assert response.status_code == 409
        api_client.delete(f"/api/admin/skills/{skill_id}?force=true",
                          headers=admin_headers)

    def test_put_skill_rename_duplicate_case_insensitive_409(
            self, api_client, admin_headers):
        skill_id = _mk_skill(api_client, admin_headers)
        response = api_client.put(f"/api/admin/skills/{skill_id}",
                                  json={"name": "html"},
                                  headers=admin_headers)
        assert response.status_code == 409
        api_client.delete(f"/api/admin/skills/{skill_id}?force=true",
                          headers=admin_headers)

    def test_put_category_rename_duplicate_409(self, api_client, admin_headers):
        names = [c["name"] for c in api_client.get(
            "/api/admin/categories", headers=admin_headers).json()["items"]]
        created = api_client.post("/api/admin/categories",
                                  json={"name": _fresh("Cat")},
                                  headers=admin_headers)
        cat_id = created.json()["id"]
        response = api_client.put(f"/api/admin/categories/{cat_id}",
                                  json={"name": names[0]},
                                  headers=admin_headers)
        assert response.status_code == 409
        api_client.delete(f"/api/admin/categories/{cat_id}",
                          headers=admin_headers)

    def test_put_job_role_rename_duplicate_409(self, api_client, admin_headers):
        titles = [r["title"] for r in api_client.get(
            "/api/wizard-options").json()["job_roles"]]
        created = api_client.post("/api/admin/job-roles",
                                  json={"title": _fresh("Role")},
                                  headers=admin_headers)
        role_id = created.json()["id"]
        response = api_client.put(f"/api/admin/job-roles/{role_id}",
                                  json={"title": titles[0]},
                                  headers=admin_headers)
        assert response.status_code == 409
        api_client.delete(f"/api/admin/job-roles/{role_id}?force=true",
                          headers=admin_headers)


class TestForeignKeyValidation:

    def test_post_skill_unknown_category_400(self, api_client, admin_headers):
        response = api_client.post("/api/admin/skills", json={
            "name": _fresh("Skill"), "category_id": 999999,
        }, headers=admin_headers)
        assert response.status_code == 400
        assert "category_id" in response.json()["detail"]

    def test_put_skill_unknown_prerequisite_400(self, api_client, admin_headers):
        skill_id = _mk_skill(api_client, admin_headers)
        response = api_client.put(f"/api/admin/skills/{skill_id}",
                                  json={"prerequisite_ids": [999999]},
                                  headers=admin_headers)
        assert response.status_code == 400
        assert "prerequisite_ids" in response.json()["detail"]
        assert "[999999]" in response.json()["detail"]
        api_client.delete(f"/api/admin/skills/{skill_id}?force=true",
                          headers=admin_headers)

    def test_put_resource_unknown_skill_400(self, api_client, admin_headers):
        created = api_client.post("/api/admin/resources", json={
            "title": _fresh("Res"), "url": "https://example.com/r",
            "type": "article",
        }, headers=admin_headers)
        resource_id = created.json()["id"]
        response = api_client.put(f"/api/admin/resources/{resource_id}",
                                  json={"skill_id": 999999},
                                  headers=admin_headers)
        assert response.status_code == 400
        assert "skill_id" in response.json()["detail"]
        api_client.delete(f"/api/admin/resources/{resource_id}",
                          headers=admin_headers)

    def test_post_job_role_unknown_skill_400(self, api_client, admin_headers):
        response = api_client.post("/api/admin/job-roles", json={
            "title": _fresh("Role"), "skill_ids": [999999],
        }, headers=admin_headers)
        assert response.status_code == 400
        assert "skill_ids" in response.json()["detail"]


class TestGraphRules:

    def test_put_category_self_parent_400(self, api_client, admin_headers):
        created = api_client.post("/api/admin/categories",
                                  json={"name": _fresh("Cat")},
                                  headers=admin_headers)
        cat_id = created.json()["id"]
        response = api_client.put(f"/api/admin/categories/{cat_id}",
                                  json={"parent_id": cat_id},
                                  headers=admin_headers)
        assert response.status_code == 400
        api_client.delete(f"/api/admin/categories/{cat_id}",
                          headers=admin_headers)

    def test_put_category_ancestor_cycle_400(self, api_client, admin_headers):
        c1 = api_client.post("/api/admin/categories",
                             json={"name": _fresh("Cat")}, headers=admin_headers).json()
        c2 = api_client.post("/api/admin/categories", json={
            "name": _fresh("Cat"), "parent_id": c1["id"],
        }, headers=admin_headers).json()
        response = api_client.put(f"/api/admin/categories/{c1['id']}",
                                  json={"parent_id": c2["id"]},
                                  headers=admin_headers)
        assert response.status_code == 400
        api_client.delete(f"/api/admin/categories/{c2['id']}", headers=admin_headers)
        api_client.delete(f"/api/admin/categories/{c1['id']}", headers=admin_headers)

    def test_put_skill_self_prerequisite_400(self, api_client, admin_headers):
        skill_id = _mk_skill(api_client, admin_headers)
        response = api_client.put(f"/api/admin/skills/{skill_id}",
                                  json={"prerequisite_ids": [skill_id]},
                                  headers=admin_headers)
        assert response.status_code == 400
        api_client.delete(f"/api/admin/skills/{skill_id}?force=true",
                          headers=admin_headers)

    def test_put_skill_prerequisite_cycle_400(self, api_client, admin_headers):
        s1 = _mk_skill(api_client, admin_headers)
        s2 = _mk_skill(api_client, admin_headers)
        first = api_client.put(f"/api/admin/skills/{s1}",
                               json={"prerequisite_ids": [s2]},
                               headers=admin_headers)
        assert first.status_code == 200, first.text
        response = api_client.put(f"/api/admin/skills/{s2}",
                                  json={"prerequisite_ids": [s1]},
                                  headers=admin_headers)
        assert response.status_code == 400
        api_client.delete(f"/api/admin/skills/{s1}?force=true", headers=admin_headers)
        api_client.delete(f"/api/admin/skills/{s2}?force=true", headers=admin_headers)


class TestRestrictedDeletes:

    def test_delete_skill_with_dependents_409_shape(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        other = _mk_skill(api_client, admin_headers)
        assert api_client.put(f"/api/admin/skills/{other}",
                              json={"prerequisite_ids": [sid]},
                              headers=admin_headers).status_code == 200
        resource = api_client.post("/api/admin/resources", json={
            "title": _fresh("Res"), "url": "https://example.com/x",
            "type": "article", "skill_id": sid,
        }, headers=admin_headers).json()
        role = api_client.post("/api/admin/job-roles", json={
            "title": _fresh("Role"), "skill_ids": [sid],
        }, headers=admin_headers).json()
        response = api_client.delete(f"/api/admin/skills/{sid}",
                                     headers=admin_headers)
        assert response.status_code == 409
        detail = response.json()["detail"]
        dependents = detail["dependents"]
        assert dependents["resources"] >= 1
        assert dependents["job_role_skills"] >= 1
        assert dependents["required_by"] >= 1
        assert isinstance(detail["message"], str)
        api_client.delete(f"/api/admin/job-roles/{role['id']}?force=true",
                          headers=admin_headers)
        api_client.delete(f"/api/admin/skills/{sid}?force=true", headers=admin_headers)
        api_client.delete(f"/api/admin/resources/{resource['id']}",
                          headers=admin_headers)
        api_client.delete(f"/api/admin/skills/{other}", headers=admin_headers)

    def test_delete_category_with_skills_409(self, api_client, admin_headers):
        cat = api_client.post("/api/admin/categories",
                              json={"name": _fresh("Cat")},
                              headers=admin_headers).json()
        sid = _mk_skill(api_client, admin_headers)
        api_client.put(f"/api/admin/skills/{sid}", json={"category_id": cat["id"]},
                       headers=admin_headers)
        response = api_client.delete(f"/api/admin/categories/{cat['id']}",
                                     headers=admin_headers)
        assert response.status_code == 409
        assert response.json()["detail"]["dependents"]["skills"] >= 1
        api_client.delete(f"/api/admin/skills/{sid}?force=true", headers=admin_headers)
        api_client.delete(f"/api/admin/categories/{cat['id']}", headers=admin_headers)

    def test_delete_job_role_with_mappings_409(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        role = api_client.post("/api/admin/job-roles", json={
            "title": _fresh("Role"), "skill_ids": [sid],
        }, headers=admin_headers).json()
        response = api_client.delete(f"/api/admin/job-roles/{role['id']}",
                                     headers=admin_headers)
        assert response.status_code == 409
        assert response.json()["detail"]["dependents"]["job_role_skills"] == 1
        api_client.delete(f"/api/admin/job-roles/{role['id']}?force=true",
                          headers=admin_headers)
        api_client.delete(f"/api/admin/skills/{sid}", headers=admin_headers)


class TestForceDeletes:

    def test_force_delete_skill_with_dependents_succeeds(
            self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        resource = api_client.post("/api/admin/resources", json={
            "title": _fresh("Res"), "url": "https://example.com/y",
            "type": "article", "skill_id": sid,
        }, headers=admin_headers).json()
        role = api_client.post("/api/admin/job-roles", json={
            "title": _fresh("Role"), "skill_ids": [sid],
        }, headers=admin_headers).json()
        response = api_client.delete(f"/api/admin/skills/{sid}?force=true",
                                     headers=admin_headers)
        assert response.status_code == 200
        remaining_resources = api_client.get("/api/admin/resources",
                                             headers=admin_headers).json()
        detached = next(r for r in remaining_resources if r["id"] == resource["id"])
        assert detached["skill_id"] is None
        titles = [r["title"] for r in api_client.get(
            "/api/wizard-options").json()["job_roles"]]
        assert role["title"] in titles
        api_client.delete(f"/api/admin/job-roles/{role['id']}?force=true",
                          headers=admin_headers)
        api_client.delete(f"/api/admin/resources/{resource['id']}",
                          headers=admin_headers)

    def test_force_delete_category_detaches_skills(self, api_client, admin_headers):
        cat = api_client.post("/api/admin/categories",
                              json={"name": _fresh("Cat")},
                              headers=admin_headers).json()
        sid = _mk_skill(api_client, admin_headers)
        api_client.put(f"/api/admin/skills/{sid}", json={"category_id": cat["id"]},
                       headers=admin_headers)
        response = api_client.delete(
            f"/api/admin/categories/{cat['id']}?force=true", headers=admin_headers)
        assert response.status_code == 200
        skill = next(s for s in api_client.get(
            "/api/admin/skills?page_size=1000", headers=admin_headers)
            .json()["items"] if s["id"] == sid)
        assert skill["category_id"] is None
        api_client.delete(f"/api/admin/skills/{sid}", headers=admin_headers)

    def test_force_delete_job_role_clears_mappings(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        role = api_client.post("/api/admin/job-roles", json={
            "title": _fresh("Role"), "skill_ids": [sid],
        }, headers=admin_headers).json()
        response = api_client.delete(
            f"/api/admin/job-roles/{role['id']}?force=true", headers=admin_headers)
        assert response.status_code == 200
        titles = [r["title"] for r in api_client.get(
            "/api/wizard-options").json()["job_roles"]]
        assert role["title"] not in titles
        api_client.delete(f"/api/admin/skills/{sid}", headers=admin_headers)


class TestIntegritySafetyNet:

    def test_duplicate_junction_insert_returns_409(self, api_client, admin_headers):
        """Duplicate skill_ids blow the job_role_skills composite PK; the
        centralized IntegrityError handler must surface 409, not 500."""
        response = api_client.post("/api/admin/job-roles", json={
            "title": _fresh("Role"), "skill_ids": [1, 1],
        }, headers=admin_headers)
        assert response.status_code == 409, response.text

    def test_db_still_usable_after_conflict(self, api_client, admin_headers):
        response = api_client.get("/api/admin/skills", headers=admin_headers)
        assert response.status_code == 200
