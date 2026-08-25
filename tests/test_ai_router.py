"""tests/test_ai_router.py — generation endpoints w/ inline jobs."""
import pytest

from backend.entities.assessment import Assessment, AssessmentQuestion
from backend.events import publisher
from backend.routers import ai as ai_router


def _purge(db_session):
    """Delete [AI]-titled assessments (+questions) in one pass.

    Shared by the before/after halves of purge_ai_rows below.
    """
    ai_ids = db_session.query(Assessment.id).filter(
        Assessment.title.like("[AI]%"))
    db_session.query(AssessmentQuestion).filter(
        AssessmentQuestion.assessment_id.in_(ai_ids)).delete(
        synchronize_session=False)
    db_session.query(Assessment).filter(
        Assessment.title.like("[AI]%")).delete(synchronize_session=False)
    db_session.commit()


@pytest.fixture(autouse=True)
def purge_ai_rows(db_session):
    """Delete [AI]-titled assessments before AND after each test so later
    suites see exact seed counts (test_schema.py pins eight table totals;
    mirrors the test_ai_repo.py cleanup contract)."""
    _purge(db_session)
    yield
    _purge(db_session)


@pytest.fixture
def inline_jobs(monkeypatch):
    """Run job bodies synchronously and capture send_event calls.

    Replaces threads + records SSE emissions for assertions.
    """
    sent = []
    monkeypatch.setattr(ai_router, "_spawn", lambda fn: fn())
    monkeypatch.setattr(publisher, "send_event",
                        lambda uid, t, d=None: sent.append((uid, t, d)))
    return sent


def _headers(api_client):
    """Login as veteran and return bearer headers.

    Mirrors conftest user_token fixture inline for locality.
    """
    tok = api_client.post("/api/auth/token", data={
        "username": "veteran@skillsynth.io",
        "password": "Veteran@123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_wizard_quiz_requires_auth(api_client):
    """Unauthenticated POST is rejected before any gating."""
    assert api_client.post("/api/ai/wizard-quiz",
                           json={"goal": "x"}).status_code == 401


def test_disabled_returns_503(api_client, monkeypatch):
    """Flag-off short-circuits with explicit 503."""
    monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", False)
    r = api_client.post("/api/ai/wizard-quiz", json={"goal": "Frontend"},
                        headers=_headers(api_client))
    assert r.status_code == 503


def test_unknown_goal_returns_404(api_client, monkeypatch):
    """Flag-on with an unknown role → 404 before any job spawn."""
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    r = api_client.post("/api/ai/wizard-quiz", json={"goal": "No Such Role"},
                        headers=_headers(api_client))
    assert r.status_code == 404


def test_wizard_quiz_flow(api_client, inline_jobs, monkeypatch):
    """Happy path: plain-dict job_id → inline worker emits ai_quiz_ready
    to the requesting user with contract-shaped ids grouped per skill."""
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    monkeypatch.setattr(ai_router.pipe, "generate_role_quiz", lambda *a, **k: [
        {"skill": "JavaScript", "text": "js?", "options":
         ["a", "b", "c", "d"], "correct_index": 1},
        {"skill": "JavaScript", "text": "js2?", "options":
         ["a", "b", "c", "d"], "correct_index": 2},
        {"skill": "HTML", "text": "html?", "options":
         ["w", "x", "y", "z"], "correct_index": 0},
    ])
    headers = _headers(api_client)
    uid = api_client.get("/api/auth/me", headers=headers).json()["id"]
    r = api_client.post("/api/ai/wizard-quiz",
                        json={"goal": "Frontend Developer"},
                        headers=headers)
    assert r.status_code == 200 and "job_id" in r.json()
    ready = [e for e in inline_jobs if e[1] == "ai_quiz_ready"]
    assert ready and ready[0][0] == uid
    qs = ready[0][2]["questions"]
    assert [q["id"] for q in qs] == ["javascript_q0", "javascript_q1",
                                     "html_q0"]


def test_practice_test_persists(api_client, inline_jobs, monkeypatch,
                                db_session):
    """Practice flow persists an [AI]-prefixed assessment and emits id."""
    from backend.repositories import catalog_repository
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    monkeypatch.setattr(ai_router.pipe, "generate_skill_quiz",
                        lambda *a, **k: [
                            {"text": "new-q", "options": ["a", "b", "c", "d"],
                             "correct_index": 2}])
    skills = catalog_repository.get_all_skills(db_session)
    sid = skills[0].id
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": sid, "n_questions": 1},
                        headers=_headers(api_client))
    assert r.status_code == 200 and "job_id" in r.json()
    ev = [e for e in inline_jobs if e[1] == "ai_test_ready"][0]
    aid = ev[2]["assessment_id"]
    assert ev[2]["skill_id"] == sid
    from backend.repositories import assess_repository as arepo
    a = arepo.get_assessment(db_session, aid)
    assert a.title.startswith("[AI]") and a.skill_id == sid


def test_practice_test_unknown_skill_404(api_client, monkeypatch):
    """Unknown skill_id → 404 before any job spawn."""
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": 999999},
                        headers=_headers(api_client))
    assert r.status_code == 404


def test_practice_test_failed_event(api_client, inline_jobs, monkeypatch,
                                    db_session):
    """Pipeline failure surfaces as ai_test_failed with clamped error."""
    from backend.repositories import catalog_repository
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", True)

    def boom(*a, **k):
        raise RuntimeError("engine exploded " + "x" * 300)

    monkeypatch.setattr(ai_router.pipe, "generate_skill_quiz", boom)
    skills = catalog_repository.get_all_skills(db_session)
    sid = skills[0].id
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": sid, "n_questions": 3},
                        headers=_headers(api_client))
    assert r.status_code == 200
    failed = [e for e in inline_jobs if e[1] == "ai_test_failed"]
    assert failed and len(failed[0][2]["error"]) <= 200
