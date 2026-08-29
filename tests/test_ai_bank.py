"""tests/test_ai_bank.py — ephemeral AI answer-key grading + narrative fix."""
import pytest

from backend.events import publisher
from backend.routers import ai as ai_router
from backend.services import settings_service


@pytest.fixture(autouse=True)
def clean_bank():
    """Keep AI_QUIZ_BANK empty around every test (module-global state)."""
    getattr(ai_router, "AI_QUIZ_BANK", {}).clear()
    yield
    getattr(ai_router, "AI_QUIZ_BANK", {}).clear()


@pytest.fixture
def inline_jobs(monkeypatch):
    """Run job bodies synchronously and capture send_event calls."""
    sent = []
    monkeypatch.setattr(ai_router, "_spawn", lambda fn: fn())
    monkeypatch.setattr(publisher, "send_event",
                        lambda uid, t, d=None: sent.append((uid, t, d)))
    return sent


def _headers(api_client):
    tok = api_client.post("/api/auth/token", data={
        "username": "veteran@skillsynth.io",
        "password": "Veteran@123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _auth_uid(api_client, headers):
    return api_client.get("/api/auth/me", headers=headers).json()["id"]


def _profile(db, uid):
    from backend.entities.learning import UserSkill
    db.commit()
    rows = db.query(UserSkill).filter(UserSkill.user_id == uid).all()
    return {(r.skill_id, r.proficiency_level) for r in rows}


def test_analyze_diagnostic_normalizes_gap_key(monkeypatch):
    """Finding 1: report rows carry gap_to_mastery; the prompt needs gap.

    Without pipeline-owned normalization the template raises KeyError,
    the broad except swallows it, and narrative_available stays false.
    """
    from backend.services import llm_pipeline

    captured = {}

    def fake_complete(contract, **k):
        captured["user"] = contract["user"]
        return {"summary": "s", "strengths": [], "weaknesses": [],
                "recommended_focus": [], "next_steps": ""}

    monkeypatch.setattr(llm_pipeline, "_engine_available", lambda: True)
    monkeypatch.setattr(llm_pipeline, "_complete_json", fake_complete)
    rows = [{"skill": "JavaScript", "correct": 1, "total": 2,
             "assessed_level": 3, "gap_to_mastery": 2}]
    out = llm_pipeline.analyze_diagnostic(rows)
    assert out is not None and out["summary"] == "s"
    assert "gap 2" in captured["user"]


def test_ai_quiz_grades_via_bank_with_narrative(
        api_client, db_session, inline_jobs, monkeypatch):
    """t1: enrichment quiz delivery banks correct indices via AI_QUIZ_BANK;
    analysis grades from the bank (correct=2/total=2/level=5) + narrative."""
    from backend.config import app_settings as settings
    from backend.services import llm_engine, llm_pipeline
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
    monkeypatch.setattr(llm_engine, "available", lambda: True)
    monkeypatch.setattr(ai_router.pipe, "generate_role_quiz", lambda *a, **k: [
        {"skill": "JavaScript", "text": "js1?", "options":
         ["a", "b", "c", "d"], "correct_index": 1},
        {"skill": "JavaScript", "text": "js2?", "options":
         ["a", "b", "c", "d"], "correct_index": 1},
    ])
    headers = _headers(api_client)
    r = api_client.post("/api/ai/wizard-quiz",
                        json={"goal": "Frontend Developer", "enrich": True},
                        headers=headers)
    assert r.status_code == 200, r.text
    job_id = r.json()["job_id"]
    assert [e for e in inline_jobs if e[1] == "ai_quiz_ready"]
    assert ai_router.AI_QUIZ_BANK[job_id]["javascript"] == [1, 1]
    monkeypatch.setattr(llm_pipeline, "_engine_available", lambda: True)
    canned = {"summary": "ok", "strengths": [], "weaknesses": [],
              "recommended_focus": [], "next_steps": ""}
    monkeypatch.setattr(llm_pipeline, "analyze_diagnostic",
                        lambda rows, *a, **k: dict(canned))
    r2 = api_client.post("/api/wizard/analysis", headers=headers, json={
        "goal": "Frontend Developer", "weekly_hours": 10,
        "answers": {"javascript_q0": 1, "javascript_q1": 1},
        "quiz_job_id": job_id})
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["narrative_available"] is True
    assert body["narrative"]["summary"] == "ok"
    row = next(p for p in body["per_skill"] if p["skill"] == "JavaScript")
    assert row["correct"] == 2 and row["total"] == 2
    assert row["assessed_level"] == 5


def test_unknown_quiz_job_falls_back_to_seeded(api_client, db_session,
                                               monkeypatch):
    """t2: unknown quiz_job_id → legacy seeded scoring; still zero writes."""
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", False)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: False)
    headers = _headers(api_client)
    uid = _auth_uid(api_client, headers)
    before = _profile(db_session, uid)
    r = api_client.post("/api/wizard/analysis", headers=headers, json={
        "goal": "Frontend Developer", "weekly_hours": 10,
        "answers": {}, "quiz_job_id": "no-such-job"})
    assert r.status_code == 200
    body = r.json()
    assert body["narrative"] is None and body["narrative_available"] is False
    assert _profile(db_session, uid) == before
