"""tests/test_ai_router.py — seeded-bank synchronous delivery + opt-in enrich."""
import pytest

from backend.entities.assessment import Assessment, AssessmentQuestion
from backend.events import publisher
from backend.routers import ai as ai_router
from backend.services import settings_service


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
    suites see exact seed counts (mirrors the legacy cleanup contract)."""
    _purge(db_session)
    yield
    _purge(db_session)


@pytest.fixture
def ai_on(monkeypatch):
    """Enable AI at runtime AND make the enrichment gate pass (engine ready)."""
    from backend.config import app_settings as settings
    from backend.services import llm_engine
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
    monkeypatch.setattr(llm_engine, "available", lambda: True)
    monkeypatch.setattr("backend.services.llm_pipeline._engine_available",
                        lambda: False)


@pytest.fixture
def inline_jobs(monkeypatch):
    """Run job bodies synchronously and capture send_event calls."""
    sent = []
    monkeypatch.setattr(ai_router, "_spawn", lambda fn: fn())
    monkeypatch.setattr(publisher, "send_event",
                        lambda uid, t, d=None: sent.append((uid, t, d)))
    return sent


def _headers(api_client):
    """Login as veteran and return bearer headers."""
    tok = api_client.post("/api/auth/token", data={
        "username": "veteran@skillsynth.io",
        "password": "Veteran@123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_wizard_quiz_requires_auth(api_client):
    """Unauthenticated POST is rejected before any delivery."""
    assert api_client.post("/api/ai/wizard-quiz",
                           json={"goal": "x"}).status_code == 401


def test_wizard_quiz_is_synchronous_when_disabled(api_client, monkeypatch):
    """Bank-first primary path: 200 + questions even with AI off (no 503)."""
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", False)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: False)
    r = api_client.post("/api/ai/wizard-quiz",
                        json={"goal": "Frontend Developer"},
                        headers=_headers(api_client))
    assert r.status_code == 200
    body = r.json()
    assert "job_id" in body and body["questions"]
    # every delivered question has the frozen bank shape
    for q in body["questions"]:
        assert q["id"] and q["skill"] and q["text"] and q["options"]


def test_unknown_goal_returns_404(api_client):
    """Unknown role → 404 regardless of AI enablement."""
    r = api_client.post("/api/ai/wizard-quiz", json={"goal": "No Such Role"},
                        headers=_headers(api_client))
    assert r.status_code == 404


def test_wizard_quiz_enrichment_banks_and_streams(api_client, inline_jobs,
                                                  monkeypatch, db_session):
    """enrich:true + AI available spawns the LLM job: bank pre-seeded then
    replaced, per-skill more=True deltas streamed, final more=False closes."""
    from backend.services.assess_service import normalize_key
    from backend.repositories import catalog_repository

    def fake_role_quiz(role, skills, exclude_texts=frozenset(), locale="en",
                       on_skill=None):
        out = []
        for s in skills:
            name = s["name"]
            chunk = [{"text": f"E{i} {name}", "options": ["a", "b", "c", "d"],
                      "correct_index": 0} for i in range(2)]
            out.extend({"skill": name, **q} for q in chunk)
            if on_skill:
                on_skill(name, chunk)
        return out

    monkeypatch.setattr(ai_router.pipe, "generate_role_quiz", fake_role_quiz)
    headers = _headers(api_client)
    r = api_client.post("/api/ai/wizard-quiz",
                        json={"goal": "Frontend Developer", "enrich": True},
                        headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["questions"]  # bank questions returned synchronously
    # bank pre-seeded from the delivered bank questions immediately
    assert body["job_id"] in ai_router.AI_QUIZ_BANK
    # job ran (inline) and emitted per-skill deltas ending in close
    ready = [e for e in inline_jobs if e[1] == "ai_quiz_ready"]
    deltas = [ev for ev in ready if ev[2].get("more")]
    closing = [ev for ev in ready if not ev[2].get("more")]
    assert deltas and closing and closing[-1][2]["questions"] == []
    # LLM keys replaced the seeded bank (two per skill, correct=0)
    role = catalog_repository.get_job_role_by_title(db_session,
                                                    "Frontend Developer")
    skill_ids = catalog_repository.get_job_role_skill_ids(db_session, role.id)
    names = [s.name for s in catalog_repository.get_skills_by_ids(
        db_session, skill_ids)]
    for n in names:
        key = normalize_key(n).lower()
        assert ai_router.AI_QUIZ_BANK[body["job_id"]].get(key) == [0, 0]


def test_wizard_quiz_enrichment_not_spawned_when_disabled(api_client,
                                                          inline_jobs,
                                                          monkeypatch):
    """enrich:true but AI off → synchronous bank only, no job/SSE."""
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_ENABLED", False)
    monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: False)
    r = api_client.post("/api/ai/wizard-quiz",
                        json={"goal": "Frontend Developer", "enrich": True},
                        headers=_headers(api_client))
    assert r.status_code == 200
    assert not inline_jobs
    assert r.json()["job_id"] not in ai_router.AI_QUIZ_BANK


def test_practice_test_sync_returns_bank(api_client, db_session):
    """Primary practice delivery returns seeded questions + seed assessment_id."""
    from backend.repositories import catalog_repository
    skills = catalog_repository.get_all_skills(db_session)
    sid = skills[0].id
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": sid, "n_questions": 3},
                        headers=_headers(api_client))
    assert r.status_code == 200
    body = r.json()
    assert body["questions"] and body["assessment_id"] is not None
    assert body["skill_id"] == sid
    assert body["skill"] == skills[0].name
    # no [AI] assessment persisted on the primary (non-enrich) path
    from backend.repositories import assess_repository as arepo
    padded = arepo.get_all_assessments(db_session)
    assert not any(a.title.startswith("[AI]") for a in padded)


def test_practice_test_enrich_persists(api_client, inline_jobs, ai_on,
                                       monkeypatch, db_session):
    """enrich:true + AI available persists the [AI] assessment + emits id."""
    from backend.repositories import catalog_repository
    from backend.repositories import assess_repository as arepo
    monkeypatch.setattr(ai_router.pipe, "generate_skill_quiz",
                        lambda *a, **k: [
                            {"text": "new-q", "options": ["a", "b", "c", "d"],
                             "correct_index": 2}])
    skills = catalog_repository.get_all_skills(db_session)
    sid = skills[0].id
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": sid, "n_questions": 1,
                              "enrich": True},
                        headers=_headers(api_client))
    assert r.status_code == 200
    ev = [e for e in inline_jobs if e[1] == "ai_test_ready"][0]
    aid = ev[2]["assessment_id"]
    assert ev[2]["skill_id"] == sid
    a = arepo.get_assessment(db_session, aid)
    assert a.title.startswith("[AI]") and a.skill_id == sid


def test_practice_test_unknown_skill_404(api_client):
    """Unknown skill_id → 404 before any delivery."""
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": 999999},
                        headers=_headers(api_client))
    assert r.status_code == 404


def test_practice_test_failed_event(api_client, inline_jobs, ai_on,
                                    monkeypatch, db_session):
    """Enrich pipeline failure surfaces as ai_test_failed with clamped error."""
    from backend.repositories import catalog_repository

    def boom(*a, **k):
        raise RuntimeError("engine exploded " + "x" * 300)

    monkeypatch.setattr(ai_router.pipe, "generate_skill_quiz", boom)
    skills = catalog_repository.get_all_skills(db_session)
    sid = skills[0].id
    r = api_client.post("/api/ai/tests/generate",
                        json={"skill_id": sid, "n_questions": 3,
                              "enrich": True},
                        headers=_headers(api_client))
    assert r.status_code == 200
    failed = [e for e in inline_jobs if e[1] == "ai_test_failed"]
    assert failed and len(failed[0][2]["error"]) <= 200
