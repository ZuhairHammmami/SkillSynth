"""Assessment tests — question payload shape and scored submissions."""

import time

import pytest

from backend.entities.assessment import AssessmentResult
from backend.entities.learning import UserSkill

from tests.integrity_support import (
    mk_assessment, mk_skill, register_user, submit_assessment, teardown,
)


class TestQuestions:

    def test_questions_shape(self, api_client, auth_headers):
        graph = api_client.get("/api/learning/graph").json()
        html = next(n for n in graph["nodes"] if n["name"] == "HTML")
        response = api_client.get(f"/api/assessments/{html['id']}/questions",
                                  headers=auth_headers)
        assert response.status_code == 200
        questions = response.json()
        assert isinstance(questions, list)
        assert len(questions) == 5
        assert set(questions[0]) == {"id", "skill", "text", "options"}

    def test_questions_unknown_skill(self, api_client, auth_headers):
        response = api_client.get("/api/assessments/99999/questions",
                                  headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_questions_requires_auth(self, api_client):
        response = api_client.get("/api/assessments/1/questions")
        assert response.status_code == 401


class TestSubmit:

    def test_submit_updates_user_skill(self, api_client, auth_headers, admin_headers):
        assessments = api_client.get("/api/admin/assessments",
                                     headers=admin_headers).json()
        html = next(a for a in assessments if a["title"] == "HTML Assessment")
        response = api_client.post("/api/assessments/submit", json={
            "assessment_id": html["id"], "answers": [0, 1, 0, 0, 0],
        }, headers=auth_headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["score"] == 100
        assert data["passed"] is True
        assert data["total_questions"] == 5
        me = api_client.get("/api/auth/me", headers=auth_headers).json()
        assert me["skill_profile"]["HTML"] == 5

    def test_submit_invalid_assessment(self, api_client, auth_headers):
        response = api_client.post("/api/assessments/submit", json={
            "assessment_id": 99999, "answers": [],
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_submit_requires_auth(self, api_client):
        response = api_client.post("/api/assessments/submit", json={
            "assessment_id": 1, "answers": [],
        })
        assert response.status_code == 401


class TestRoleQuestions:
    """Pins GET /api/assessments/role/{title} (routers/assessments.py →
    assess_service.questions_for_skill): frozen item shape
    {id, skill, text, options}, [] for unknown roles, auth-gated."""

    def test_role_questions_happy_shape(self, api_client, auth_headers):
        response = api_client.get(
            "/api/assessments/role/Frontend Developer", headers=auth_headers)
        assert response.status_code == 200
        questions = response.json()
        assert isinstance(questions, list) and questions
        assert set(questions[0]) == {"id", "skill", "text", "options"}
        assert isinstance(questions[0]["options"], list)

    def test_role_questions_unknown_role_empty(self, api_client, auth_headers):
        response = api_client.get(
            "/api/assessments/role/NonexistentRole", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_role_questions_requires_auth(self, api_client):
        response = api_client.get("/api/assessments/role/Frontend Developer")
        assert response.status_code == 401


class TestSubmitDepth:
    """Scored-submission depth pins (services/assess_service.submit_result:
    score = round(correct/total*100), passed = score >= pass_score,
    proficiency = round(correct/total*5); persistence via
    assess_repository.create_result + upsert_user_skill)."""

    def test_partial_score_fails_with_proportional_proficiency(
            self, api_client, admin_headers, db_session):
        """1/2 correct → score 50 < pass_score 60 → passed False; the
        user_skills proficiency is round(0.5*5)=2 and one assessment_results
        row is persisted with that score."""
        skill = mk_skill(api_client, admin_headers)
        assessment = mk_assessment(db_session, skill)
        user_id, headers = register_user(api_client)
        try:
            payload = api_client.post("/api/assessments/submit", json={
                "assessment_id": assessment, "answers": [0, 1]},
                headers=headers).json()
            assert payload["score"] == 50
            assert payload["passed"] is False
            db_session.expire_all()
            result = db_session.query(AssessmentResult).filter_by(
                user_id=user_id, assessment_id=assessment).one()
            assert result.score == 50 and result.passed is False
            assert db_session.get(UserSkill, (user_id, skill)).proficiency_level == 2
        finally:
            teardown(api_client, admin_headers, {
                "users": [user_id], "assessments": [assessment],
                "skills": [skill]})

    def test_boundary_score_equals_pass_score_passes(
            self, api_client, admin_headers, db_session):
        """3/5 correct → score 60 == pass_score 60 → passed True (>=
        boundary in submit_result); proficiency rounds to 3."""
        skill = mk_skill(api_client, admin_headers)
        assessment = mk_assessment(db_session, skill, n_questions=5)
        user_id, headers = register_user(api_client)
        try:
            payload = api_client.post("/api/assessments/submit", json={
                "assessment_id": assessment,
                "answers": [0, 0, 0, 1, 1]}, headers=headers).json()
            assert payload["score"] == 60
            assert payload["passed"] is True
            db_session.expire_all()
            result = db_session.query(AssessmentResult).filter_by(
                user_id=user_id, assessment_id=assessment).one()
            assert result.passed is True
            assert db_session.get(UserSkill, (user_id, skill)).proficiency_level == 3
        finally:
            teardown(api_client, admin_headers, {
                "users": [user_id], "assessments": [assessment],
                "skills": [skill]})

    def test_resubmit_upserts_one_user_skills_row(
            self, api_client, admin_headers, db_session):
        """A second attempt keeps exactly ONE user_skills row (composite-PK
        upsert) with last_assessed_at refreshed, while attempts accumulate
        as separate assessment_results history rows."""
        skill = mk_skill(api_client, admin_headers)
        assessment = mk_assessment(db_session, skill)
        user_id, headers = register_user(api_client)
        try:
            submit_assessment(api_client, headers, assessment)
            db_session.expire_all()
            # Snapshot the primitive: identity map returns one shared
            # instance per PK, so holding the ORM object would compare
            # the refreshed attribute against itself.
            first_stamp = db_session.get(
                UserSkill, (user_id, skill)).last_assessed_at
            time.sleep(0.02)
            submit_assessment(api_client, headers, assessment)
            db_session.expire_all()
            rows = db_session.query(UserSkill).filter_by(
                user_id=user_id, skill_id=skill).all()
            assert len(rows) == 1
            assert rows[0].last_assessed_at > first_stamp
            assert rows[0].proficiency_level == 5
            assert db_session.query(AssessmentResult).filter_by(
                user_id=user_id, assessment_id=assessment).count() == 2
        finally:
            teardown(api_client, admin_headers, {
                "users": [user_id], "assessments": [assessment],
                "skills": [skill]})

    def test_submit_empty_questions_assessment_rejected_400(
            self, api_client, admin_headers, db_session):
        """An assessment with zero assessment_questions rows maps to 400
        ("Assessment has no questions") instead of dividing by zero."""
        skill = mk_skill(api_client, admin_headers)
        assessment = mk_assessment(db_session, skill, n_questions=0)
        user_id, headers = register_user(api_client)
        try:
            response = api_client.post("/api/assessments/submit", json={
                "assessment_id": assessment, "answers": []},
                headers=headers)
            assert response.status_code == 400, response.text
        finally:
            teardown(api_client, admin_headers, {
                "users": [user_id], "assessments": [assessment],
                "skills": [skill]})
