"""Backend tests for the AI placement quiz → wizard analysis contract.

Covers: wizard-quiz job creation (answer-key bank), grading via
/wizard/analysis with quiz_job_id, and the 503 gate when AI is off.
The real LLM engine is mocked so no model is ever invoked.
"""
import time

import pytest

from backend.routers import ai as ai_router
from backend.routers.ai import AI_QUIZ_BANK
from backend.services import settings_service


def _fake_role_quiz(role_title, skills, exclude_texts=frozenset(),
                    proficiency_level=None, topics=None, locale="en"):
    """Deterministic role quiz: two MCQs per requested skill, correct=0.

    Replaces llm_pipeline.generate_role_quiz in tests; the wizard job
    converts each tag to a q0/q1 id and records correct_index in the bank.
    """
    out = []
    for s in skills:
        name = s["name"]
        for i in range(2):
            out.append({"skill": name, "text": f"Q{i} {name}",
                        "options": ["A", "B", "C", "D"], "correct_index": 0})
    return out


@pytest.fixture
def ai_on(monkeypatch):
    """Enable AI at runtime and mock the quiz generator; restore after."""
    prev = settings_service.is_ai_enabled()
    settings_service.set_ai_enabled(True)
    monkeypatch.setattr("backend.services.llm_pipeline.generate_role_quiz",
                        _fake_role_quiz)
    monkeypatch.setattr("backend.services.llm_pipeline._engine_available",
                        lambda: False)
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


def test_wizard_quiz_creates_bank_entry(api_client, user_token, ai_on):
    """POST /ai/wizard-quiz returns a job and populates the answer-key bank."""
    goal = _first_role(api_client)
    resp = api_client.post("/api/ai/wizard-quiz", json={"goal": goal},
                           headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200, resp.text
    job_id = resp.json()["job_id"]
    assert _wait_for_bank(job_id)
    assert all(isinstance(v, list) for v in AI_QUIZ_BANK[job_id].values())


def test_quiz_analysis_grades_per_skill(api_client, user_token, ai_on):
    """Analysis with quiz_job_id grades per-skill levels + weaknesses."""
    goal = _first_role(api_client)
    job_id = api_client.post("/api/ai/wizard-quiz", json={"goal": goal},
                             headers={"Authorization": f"Bearer {user_token}"}).json()["job_id"]
    assert _wait_for_bank(job_id)
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
    assert body["per_skill"], "per_skill must be populated"
    assert all(isinstance(r["assessed_level"], int) for r in body["per_skill"])
    assert body["weaknesses"], "graded skills should yield weaknesses"
    assert body["recommended_focus"], "recommended_focus should be populated"


def test_wizard_quiz_disabled_returns_503(api_client, user_token):
    """With AI off, /ai/wizard-quiz degrades to 503 and bank stays empty."""
    prev = settings_service.is_ai_enabled()
    settings_service.set_ai_enabled(False)
    try:
        goal = _first_role(api_client)
        resp = api_client.post("/api/ai/wizard-quiz", json={"goal": goal},
                               headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 503
    finally:
        settings_service.set_ai_enabled(prev)
