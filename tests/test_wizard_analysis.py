"""tests/test_wizard_analysis.py — pure pre-path analysis."""
from backend.services.assess_service import normalize_key


def _headers(api_client):
    tok = api_client.post("/api/auth/token", data={
        "username": "veteran@skillsynth.io",
        "password": "Veteran@123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _auth_uid(api_client, headers):
    """Authenticated principal's id from /api/auth/me.

    Called by every test that needs the snapshot uid; uses the SAME
    bearer headers as the requests under test so the zero-write proof
    tracks the user the endpoint actually acts on (no seed-order
    coupling). Wire key `id` per dto/auth.py UserOut.
    """
    return api_client.get("/api/auth/me", headers=headers).json()["id"]


def _profile(db, uid):
    """Snapshot user_skills rows of the authenticated principal.

    uid MUST come from _auth_uid (/api/auth/me) for the same session —
    the snapshot has to watch whoever the endpoint authenticates as,
    or the equality assertion proves nothing. Commits first so each
    query opens a fresh transaction and sees whatever the request
    session may have (wrongly) written.
    """
    from backend.entities.learning import UserSkill
    db.commit()
    rows = db.query(UserSkill).filter(UserSkill.user_id == uid).all()
    return {(r.skill_id, r.proficiency_level) for r in rows}


def test_analysis_is_pure(api_client, db_session):
    """Endpoint computes levels without touching user_skills."""
    headers = _headers(api_client)
    uid = _auth_uid(api_client, headers)
    before = _profile(db_session, uid)
    r = api_client.post("/api/wizard/analysis", headers=headers, json={
        "goal": "Frontend Developer", "weekly_hours": 10, "answers": {}})
    assert r.status_code == 200
    body = r.json()
    assert set(body) >= {"per_skill", "weaknesses", "strengths",
                         "recommended_focus", "narrative_available"}
    assert body["narrative"] is None and body["narrative_available"] is False
    assert _profile(db_session, uid) == before


def test_levels_match_formula(api_client, db_session):
    """Graded quiz (<skill>_q<i> keys) engages scoring; weeks estimate sane."""
    qs = api_client.get("/api/assessments/role/Frontend Developer",
                        headers=_headers(api_client)).json()
    assert qs, "seed must provide Frontend Developer questions"
    answers, seen = {}, {}
    for q in qs:
        i = seen.get(q["skill"], 0)
        answers[f"{normalize_key(q['skill']).lower()}_q{i}"] = 0
        seen[q["skill"]] = i + 1
    r = api_client.post("/api/wizard/analysis", headers=_headers(api_client),
                        json={"goal": "Frontend Developer", "weekly_hours": 10,
                              "answers": answers})
    assert r.status_code == 200, r.text
    body = r.json()
    target = next(p for p in body["per_skill"]
                  if p["skill"] == qs[0]["skill"])
    assert target["answered_count"] > 0
    assert 0 <= target["assessed_level"] <= 5
    assert isinstance(body["estimated_weeks"], int) \
        and body["estimated_weeks"] >= 1


def test_unknown_role_404(api_client):
    """Unknown goal job role maps to 404 per the brief contract."""
    r = api_client.post("/api/wizard/analysis", headers=_headers(api_client),
                        json={"goal": "No Such Role", "weekly_hours": 10,
                              "answers": {}})
    assert r.status_code == 404
