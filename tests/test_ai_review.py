"""tests/test_ai_review.py — /ai/explain endpoint + bounded submit hook."""
import pytest

from backend.services import assess_service, settings_service

_MARK = "[REVIEW]"
_TRACK = {"assessments": [], "skills": []}


@pytest.fixture(autouse=True)
def purge_review_rows(db_session):
    """Delete this module's rows so pinned seed counts stay green.

    Mirrors tests/test_ai_repo.py: removes created assessments with
    their questions/results, any UserSkill rows the submit hook added
    for the authed veteran on touched skills, and every
    ai_proficiency_review activity row (action exclusive to SS-AI).
    """
    from backend.entities.assessment import (
        Assessment, AssessmentQuestion, AssessmentResult)
    from backend.entities.engagement import ActivityLog
    from backend.entities.identity import User
    from backend.entities.learning import UserSkill
    yield
    ids = list(_TRACK["assessments"])
    if ids:
        db_session.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id.in_(ids)).delete(
            synchronize_session=False)
        db_session.query(AssessmentResult).filter(
            AssessmentResult.assessment_id.in_(ids)).delete(
            synchronize_session=False)
        db_session.query(Assessment).filter(
            Assessment.id.in_(ids)).delete(synchronize_session=False)
    veteran = db_session.query(User).filter_by(
        email="veteran@skillsynth.io").first()
    if _TRACK["skills"] and veteran:
        db_session.query(UserSkill).filter(
            UserSkill.user_id == veteran.id,
            UserSkill.skill_id.in_(_TRACK["skills"])).delete(
            synchronize_session=False)
    db_session.query(ActivityLog).filter(
        ActivityLog.action == "ai_proficiency_review").delete(
        synchronize_session=False)
    db_session.commit()
    _TRACK["assessments"].clear()
    _TRACK["skills"].clear()


def _headers(api_client, who=("veteran@skillsynth.io", "Veteran@123456")):
    """Bearer headers for a seeded account (default veteran).

    Used by every request-level test in this module.
    """
    tok = api_client.post("/api/auth/token", data={
        "username": who[0], "password": who[1]}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _mk_assessment(db, skill_id, n):
    """Insert a marker-titled assessment via arepo; tracks id for purge.

    Local mirror of integrity_support.mk_assessment built on
    assess_repository.create_assessment_with_questions; consumed by the
    explain and submit-hook tests below.
    """
    from backend.repositories import assess_repository as arepo
    a = arepo.create_assessment_with_questions(
        db, skill_id, f"{_MARK} probe", "d", 60,
        [{"text": f"q{i}", "options": ["a", "b", "c", "d"],
          "correct_index": 0} for i in range(n)])
    _TRACK["assessments"].append(a.id)
    return a


def _untouched_skill(db, user_id):
    """First seed skill lacking a user_skills row for user_id.

    Used by the submit-hook tests so the purge fixture only removes
    rows those tests created (seeded proficiency data stays intact).
    """
    from backend.entities.learning import UserSkill
    from backend.repositories import catalog_repository
    taken = {sid for (sid,) in db.query(UserSkill.skill_id).filter(
        UserSkill.user_id == user_id).all()}
    return next(s for s in catalog_repository.get_all_skills(db)
                if s.id not in taken)


class TestExplain:

    def test_explain_static_fallback(self, api_client, monkeypatch):
        """Pipeline None ⇒ static recap with narrative_available False.

        Pins the fallback branch of routers/ai.explain_result when
        llm_pipeline.explain_result returns None.
        """
        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
        monkeypatch.setattr("backend.services.llm_pipeline.explain_result",
                            lambda responses: None)
        r = api_client.post("/api/ai/explain", headers=_headers(api_client),
                            json={"assessment_id": 1, "answers": [0, 0]})
        body = r.json()
        assert r.status_code == 200
        assert body["narrative_available"] is False
        assert body["advice"] == ""
        assert body["explanations"][0]["question_index"] == 0
        assert body["explanations"][0]["why"]

    def test_explain_disabled_returns_503(self, api_client, monkeypatch):
        """AI_ENABLED off ⇒ 503 before any lookup (routers/ai._gate)."""
        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", False)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: False)
        r = api_client.post("/api/ai/explain", headers=_headers(api_client),
                            json={"assessment_id": 1, "answers": [0]})
        assert r.status_code == 503

    def test_explain_unknown_assessment_404(self, api_client, monkeypatch):
        """Unknown assessment id ⇒ 404 (explain_result lookup miss)."""
        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
        r = api_client.post("/api/ai/explain", headers=_headers(api_client),
                            json={"assessment_id": 9999999,
                                  "answers": [0]})
        assert r.status_code == 404

    def test_explain_empty_questions_400(self, api_client, db_session,
                                         monkeypatch):
        """Question-less assessment ⇒ 400 (explain_result gate)."""
        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
        a = _mk_assessment(db_session, None, 0)
        r = api_client.post("/api/ai/explain", headers=_headers(api_client),
                            json={"assessment_id": a.id, "answers": []})
        assert r.status_code == 400


class TestSubmitHook:
    """Bounded post-submit review (services/assess_service): spawns only
    when AI_ENABLED ∧ _engine_ready(); ±1/high-confidence policy; audit +
    SSE only on applied verdicts."""

    def test_submit_hook_applies_high_confidence(self, api_client,
                                                 db_session, monkeypatch):
        """High-confidence +1 ⇒ user_skills 3 and audit delta 1.

        Pin semantics: 4 questions answered [0,0,1,1] give formula
        round(2/4*5)=2; the fake review returns applied +1 so the final
        level is 3 and the ai_proficiency_review row records delta 1.
        Threads run synchronously here via direct-call spawn patch.
        """
        from backend.entities.engagement import ActivityLog
        from backend.entities.learning import UserSkill
        calls = {}

        def fake_review(correct, total, difficulty, attempt_no,
                        current_level):
            calls["args"] = (correct, total, difficulty, current_level)
            return {"delta": 1, "confidence": "high",
                    "rationale": "solid", "applied": True,
                    "final_level": current_level + 1}

        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
        monkeypatch.setattr(assess_service, "review_level", fake_review)
        monkeypatch.setattr(assess_service, "_spawn_review",
                            lambda fn: fn())
        headers = _headers(api_client)
        user_id = api_client.get("/api/auth/me",
                                 headers=headers).json()["id"]
        skill = _untouched_skill(db_session, user_id)
        _TRACK["skills"].append(skill.id)
        a = _mk_assessment(db_session, skill.id, 4)
        r = api_client.post("/api/assessments/submit", headers=headers,
                            json={"assessment_id": a.id,
                                  "answers": [0, 0, 1, 1]})
        assert r.status_code == 200
        db_session.expire_all()
        row = db_session.query(UserSkill).filter_by(
            user_id=user_id, skill_id=skill.id).first()
        assert row.proficiency_level == 3
        assert calls["args"] == (2, 4, skill.difficulty_level or 1, 2)
        audit = db_session.query(ActivityLog).filter_by(
            action="ai_proficiency_review").order_by(
            ActivityLog.id.desc()).first()
        assert audit is not None
        assert audit.user_id == user_id
        assert audit.entity_type == "skill"
        assert int(audit.entity_id) == skill.id
        assert audit.data["delta"] == 1
        assert audit.data["result_id"] == r.json()["id"]

    def test_submit_hook_low_confidence_keeps_formula_level(
            self, api_client, db_session, monkeypatch):
        """applied False ⇒ formula level stands and no audit row lands."""
        from backend.entities.engagement import ActivityLog
        from backend.entities.learning import UserSkill

        def fake_review(correct, total, difficulty, attempt_no,
                        current_level):
            return {"delta": 1, "confidence": "low",
                    "rationale": "unsure", "applied": False,
                    "final_level": current_level}

        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
        monkeypatch.setattr(assess_service, "review_level", fake_review)
        monkeypatch.setattr(assess_service, "_spawn_review",
                            lambda fn: fn())
        headers = _headers(api_client)
        user_id = api_client.get("/api/auth/me",
                                 headers=headers).json()["id"]
        skill = _untouched_skill(db_session, user_id)
        _TRACK["skills"].append(skill.id)
        a = _mk_assessment(db_session, skill.id, 4)
        r = api_client.post("/api/assessments/submit", headers=headers,
                            json={"assessment_id": a.id,
                                  "answers": [0, 0, 1, 1]})
        assert r.status_code == 200
        db_session.expire_all()
        row = db_session.query(UserSkill).filter_by(
            user_id=user_id, skill_id=skill.id).first()
        assert row.proficiency_level == 2
        assert db_session.query(ActivityLog).filter_by(
            action="ai_proficiency_review").count() == 0

    def test_submit_hook_skipped_when_engine_unready(
            self, api_client, db_session, monkeypatch):
        """_engine_ready False ⇒ review seam never invoked, level 2."""
        from backend.entities.learning import UserSkill

        def boom(*args):
            raise AssertionError("review_level must not run")

        monkeypatch.setattr("backend.config.app_settings.AI_ENABLED", True)
        monkeypatch.setattr(settings_service, "is_ai_enabled", lambda: True)
        monkeypatch.setattr("backend.services.llm_pipeline.review_level",
                            boom)
        monkeypatch.setattr(assess_service, "_engine_ready", lambda: False)
        monkeypatch.setattr(assess_service, "review_level", boom)
        headers = _headers(api_client)
        user_id = api_client.get("/api/auth/me",
                                 headers=headers).json()["id"]
        skill = _untouched_skill(db_session, user_id)
        _TRACK["skills"].append(skill.id)
        a = _mk_assessment(db_session, skill.id, 4)
        r = api_client.post("/api/assessments/submit", headers=headers,
                            json={"assessment_id": a.id,
                                  "answers": [0, 0, 1, 1]})
        assert r.status_code == 200
        db_session.expire_all()
        row = db_session.query(UserSkill).filter_by(
            user_id=user_id, skill_id=skill.id).first()
        assert row.proficiency_level == 2
