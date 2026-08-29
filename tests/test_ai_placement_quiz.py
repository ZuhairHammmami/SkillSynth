"""Backend tests for the AI ENRICHMENT placement quiz → wizard analysis.

Covers: enrich wizard-quiz job (answer-key bank pre-seeded from the bank then
replaced by the LLM), bank grading via /wizard/analysis with quiz_job_id, and
the fact that the primary (non-enrich) path is synchronous with no 503 gate.
The real LLM engine is mocked so no model is ever invoked.
"""
import time

import pytest

from backend.routers import ai as ai_router
from backend.routers.ai import AI_QUIZ_BANK
from backend.services import settings_service


def _fake_role_quiz(role_title, skills, exclude_texts=frozenset(),
                    proficiency_level=None, topics=None, locale="en",
                    on_skill=None):
    """Deterministic role quiz: two MCQs per requested skill, correct=0.

    Replaces llm_pipeline.generate_role_quiz in enrichment tests; the job
    converts each tag to a q0/q1 id and records correct_index in the bank.
    """
    out = []
    for s in skills:
        name = s["name"]
        chunk = [{"text": f"Q{i} {name}", "options": ["A", "B", "C", "D"],
                  "correct_index": 0} for i in range(2)]
        out.extend({"skill": name, **q} for q in chunk)
        if on_skill:
            on_skill(name, chunk)
    return out


@pytest.fixture
def ai_on(monkeypatch):
    """Enable AI at runtime, make enrichment available, mock the generator.

    Also pins llm_pipeline._engine_available False so the narrative hook
    (analyze_diagnostic) never triggers a real inference load during tests.
    """
    prev = settings_service.is_ai_enabled()
    settings_service.set_ai_enabled(True)
    monkeypatch.setattr(ai_router, "_spawn", lambda fn: fn())
    monkeypatch.setattr("backend.services.llm_engine.available", lambda: True)
    monkeypatch.setattr("backend.services.llm_pipeline._engine_available",
                        lambda: False)
    monkeypatch.setattr("backend.services.llm_pipeline.generate_role_quiz",
                        _fake_role_quiz)
    yield
    settings_service.set_ai_enabled(prev)


def _first_role(api_client):
    """Return the title of the first seeded job role for wizard calls."""
    roles = api_client.get("/api/wizard-options").json()["job_roles"]
    return roles[0]["title"]


def _wait_for_bank(job_id, timeout=5.0):
    """Poll the in-memory answer-key bank until the job id appears."""
    for _ in range(int(timeout / 0.05)):
        if job_id in AI_QUIZ_BANK:
            return True
        time.sleep(0.05)
    return job_id in AI_QUIZ_BANK


def _enrich_bank(api_client, user_token, goal):
    """POST the enrichment wizard quiz and poll until its bank is populated."""
    resp = api_client.post("/api/ai/wizard-quiz", json={"goal": goal,
                                                        "enrich": True},
                           headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200, resp.text
    job_id = resp.json()["job_id"]
    assert _wait_for_bank(job_id), "enrichment bank never populated"
    return job_id


def _role_with_quiz(api_client, user_token, min_skills=2):
    """Return (goal, job_id) for an enrichment role with >= min_skills."""
    roles = api_client.get("/api/wizard-options").json()["job_roles"]
    for role in roles:
        goal = role["title"]
        job_id = _enrich_bank(api_client, user_token, goal)
        if len(AI_QUIZ_BANK[job_id]) >= min_skills:
            return goal, job_id
    raise AssertionError(f"no role with >= {min_skills} skills found")


def test_wizard_quiz_is_synchronous_and_bankless(api_client, user_token):
    """Primary (non-enrich) delivery returns questions, no 503, no bank."""
    prev = settings_service.is_ai_enabled()
    settings_service.set_ai_enabled(False)
    try:
        goal = _first_role(api_client)
        resp = api_client.post("/api/ai/wizard-quiz", json={"goal": goal},
                               headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["questions"] and "job_id" in body
        assert body["job_id"] not in AI_QUIZ_BANK
    finally:
        settings_service.set_ai_enabled(prev)


def test_enrich_creates_bank_entry(api_client, user_token, ai_on):
    """enrich wizard-quiz populates the answer-key bank (LLM keys)."""
    goal = _first_role(api_client)
    job_id = _enrich_bank(api_client, user_token, goal)
    assert all(isinstance(v, list) for v in AI_QUIZ_BANK[job_id].values())


def test_quiz_analysis_grades_per_skill(api_client, user_token, ai_on):
    """Bank grading yields 0 for the wrong skill, 5 for correct ones.

    The fake bank stores correct_index==0 for every enrichment question. We
    answer the FIRST skill fully wrong and every other skill fully correct, so
    only _analysis_from_bank (driven by AI_QUIZ_BANK) can produce {0, 5}.
    """
    goal, job_id = _role_with_quiz(api_client, user_token)
    answers, first = {}, True
    for key, idxs in AI_QUIZ_BANK[job_id].items():
        for i, ci in enumerate(idxs):
            answers[f"{key}_q{i}"] = (ci + 1) % 4 if first else ci
        first = False
    resp = api_client.post("/api/wizard/analysis",
                           json={"goal": goal, "weekly_hours": 10,
                                 "quiz_job_id": job_id, "answers": answers},
                           headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    levels = [r["assessed_level"] for r in body["per_skill"]]
    assert levels, "per_skill must be populated"
    assert set(levels) == {0, 5}, f"bank-only levels expected, got {levels}"
    assert body["weaknesses"], "graded skills should yield weaknesses"
    assert body["recommended_focus"], "recommended_focus should be populated"
