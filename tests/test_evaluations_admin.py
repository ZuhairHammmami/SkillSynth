"""Admin evaluations CRUD tests — assessments + questions.

Mirrors tests/test_admin.py style (api_client/admin_headers fixtures from
conftest, admin@skillsynth.io / Admin@123456). Exercises the
routers/evaluations_admin.py endpoints: assessment create/read/update/delete
and the questions sub-resource (add/edit/delete/reorder/last-guard).
"""

import uuid

import pytest

from backend.entities.assessment import (
    Assessment, AssessmentQuestion, AssessmentResult,
)
from backend.entities.catalog import Skill


def _fresh(prefix):
    """Unique token so tests never collide with seeded or parallel rows."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# Track every row this module creates so teardown restores the shared,
# session-scoped test DB to its pristine counts (the count-pinning graph
# and schema tests depend on it).
_CREATED = {"skills": [], "assessments": []}


def _mk_skill(api_client, admin_headers):
    """POST a throwaway skill (registered for teardown) and return its id."""
    resp = api_client.post("/api/admin/skills", json={"name": _fresh("Eval")},
                           headers=admin_headers)
    assert resp.status_code == 200, resp.text
    sid = resp.json()["id"]
    _CREATED["skills"].append(sid)
    return sid


def _mk_assessment(api_client, admin_headers, skill_id):
    """POST a minimal assessment (registered for teardown) and return its id."""
    resp = api_client.post("/api/admin/assessments", json={
        "skill_id": skill_id, "title": _fresh("Assessment"),
        "description": "desc", "pass_score": 70}, headers=admin_headers)
    assert resp.status_code == 200, resp.text
    aid = resp.json()["id"]
    _CREATED["assessments"].append(aid)
    return aid


@pytest.fixture(autouse=True)
def _cleanup_crud(db_session):
    """Remove this module's rows after each test, FK-safe order.

    Assessments are deleted first (their questions/results go too), then
    skills; each row is existence-checked so the API-delete tests that
    already removed their rows are no-ops here."""
    yield
    for aid in list(_CREATED["assessments"]):
        if db_session.get(Assessment, aid) is not None:
            db_session.query(AssessmentQuestion).filter_by(
                assessment_id=aid).delete()
            db_session.query(AssessmentResult).filter_by(
                assessment_id=aid).delete()
            db_session.query(Assessment).filter_by(id=aid).delete()
    for sid in list(_CREATED["skills"]):
        if db_session.get(Skill, sid) is not None:
            db_session.query(Assessment).filter_by(skill_id=sid).delete()
            db_session.query(Skill).filter_by(id=sid).delete()
    db_session.commit()
    _CREATED["skills"].clear()
    _CREATED["assessments"].clear()


class TestAssessmentCRUD:

    def test_create_happy_returns_serialized_row(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        resp = api_client.post("/api/admin/assessments", json={
            "skill_id": sid, "title": "LearnerQuiz",
            "description": "intro", "pass_score": 60}, headers=admin_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["title"] == "LearnerQuiz"
        assert data["skill_id"] == sid

    def test_create_unknown_skill_400(self, api_client, admin_headers):
        resp = api_client.post("/api/admin/assessments", json={
            "skill_id": 999999, "title": "Bad", "pass_score": 60},
            headers=admin_headers)
        assert resp.status_code == 400

    def test_get_detail_with_questions(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q1", "options": ["a", "b"], "correct_index": 1},
            headers=admin_headers)
        resp = api_client.get(f"/api/admin/assessments/{aid}",
                              headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == aid
        assert data["skill_id"] == sid
        assert len(data["questions"]) == 1
        assert data["questions"][0]["prompt"] == "Q1"

    def test_create_pass_score_zero_round_trips(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        resp = api_client.post("/api/admin/assessments", json={
            "skill_id": sid, "title": "ZeroPass", "pass_score": 0},
            headers=admin_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["passing_score"] == 0
        detail = api_client.get(
            f"/api/admin/assessments/{resp.json()['id']}",
            headers=admin_headers).json()
        assert detail["passing_score"] == 0

    def test_get_detail_missing_404(self, api_client, admin_headers):
        resp = api_client.get("/api/admin/assessments/99999999",
                              headers=admin_headers)
        assert resp.status_code == 404

    def test_update_assessment_happy(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        resp = api_client.put(f"/api/admin/assessments/{aid}",
                              json={"title": "Renamed", "pass_score": 80},
                              headers=admin_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["title"] == "Renamed"
        assert resp.json()["passing_score"] == 80

    def test_update_missing_404(self, api_client, admin_headers):
        resp = api_client.put("/api/admin/assessments/99999999",
                              json={"title": "x"}, headers=admin_headers)
        assert resp.status_code == 404

    def test_update_unknown_skill_400(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        resp = api_client.put(f"/api/admin/assessments/{aid}",
                              json={"skill_id": 999999}, headers=admin_headers)
        assert resp.status_code == 400

    def test_delete_happy(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        resp = api_client.delete(f"/api/admin/assessments/{aid}",
                                 headers=admin_headers)
        assert resp.status_code == 200

    def test_delete_restricted_by_questions_then_force(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q1", "options": ["a", "b"], "correct_index": 0},
            headers=admin_headers)
        blocked = api_client.delete(f"/api/admin/assessments/{aid}",
                                    headers=admin_headers)
        assert blocked.status_code == 409
        detail = blocked.json()["detail"]
        assert "force=true" in detail["message"]
        assert detail["dependents"]["assessment_questions"] == 1
        forced = api_client.delete(f"/api/admin/assessments/{aid}?force=true",
                                   headers=admin_headers)
        assert forced.status_code == 200, forced.text
        gone = api_client.get(f"/api/admin/assessments/{aid}",
                              headers=admin_headers)
        assert gone.status_code == 404


class TestQuestionCRUD:

    def test_add_question_happy(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        resp = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Pick one", "options": ["a", "b", "c"],
            "correct_index": 0}, headers=admin_headers)
        assert resp.status_code == 200, resp.text
        detail = api_client.get(f"/api/admin/assessments/{aid}",
                                headers=admin_headers).json()
        assert len(detail["questions"]) == 1
        assert detail["questions"][0]["position"] == 1

    def test_add_question_options_too_few_400(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        resp = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q", "options": ["only"], "correct_index": 0},
            headers=admin_headers)
        assert resp.status_code in (400, 422)

    def test_add_question_bad_correct_index_400(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        resp = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q", "options": ["a", "b"], "correct_index": 5},
            headers=admin_headers)
        assert resp.status_code == 400

    def test_add_question_unknown_assessment_404(self, api_client, admin_headers):
        resp = api_client.post("/api/admin/assessments/99999999/questions",
                               json={"prompt": "Q", "options": ["a", "b"],
                                     "correct_index": 0},
                               headers=admin_headers)
        assert resp.status_code == 404

    def test_update_question_happy(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        created = api_client.post(f"/api/admin/assessments/{aid}/questions",
                                  json={"prompt": "Q", "options": ["a", "b"],
                                        "correct_index": 0},
                                  headers=admin_headers).json()
        resp = api_client.put(
            f"/api/admin/assessments/{aid}/questions/{created['id']}",
            json={"prompt": "Edited", "options": ["x", "y", "z"],
                  "correct_index": 2}, headers=admin_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["prompt"] == "Edited"
        assert resp.json()["correct_index"] == 2

    def test_update_question_repositions_neighbors(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        api_client.post(f"/api/admin/assessments/{aid}/questions",
                        json={"prompt": "Q1", "options": ["a", "b"],
                              "correct_index": 0}, headers=admin_headers)
        q2 = api_client.post(f"/api/admin/assessments/{aid}/questions",
                             json={"prompt": "Q2", "options": ["a", "b"],
                                   "correct_index": 0},
                             headers=admin_headers).json()
        api_client.put(f"/api/admin/assessments/{aid}/questions/{q2['id']}",
                       json={"position": 1}, headers=admin_headers)
        detail = api_client.get(f"/api/admin/assessments/{aid}",
                                headers=admin_headers).json()
        positions = [q["position"] for q in detail["questions"]]
        assert sorted(positions) == [1, 2]
        assert positions == [1, 2]

    def test_delete_question_reindexes(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        q1 = api_client.post(f"/api/admin/assessments/{aid}/questions",
                             json={"prompt": "Q1", "options": ["a", "b"],
                                   "correct_index": 0},
                             headers=admin_headers).json()
        api_client.post(f"/api/admin/assessments/{aid}/questions",
                        json={"prompt": "Q2", "options": ["a", "b"],
                              "correct_index": 0}, headers=admin_headers)
        api_client.delete(f"/api/admin/assessments/{aid}/questions/{q1['id']}",
                          headers=admin_headers)
        detail = api_client.get(f"/api/admin/assessments/{aid}",
                                headers=admin_headers).json()
        assert len(detail["questions"]) == 1
        assert detail["questions"][0]["position"] == 1

    def test_delete_last_question_400(self, api_client, admin_headers):
        sid = _mk_skill(api_client, admin_headers)
        aid = _mk_assessment(api_client, admin_headers, sid)
        q = api_client.post(f"/api/admin/assessments/{aid}/questions",
                            json={"prompt": "Q", "options": ["a", "b"],
                                  "correct_index": 0},
                            headers=admin_headers).json()
        resp = api_client.delete(
            f"/api/admin/assessments/{aid}/questions/{q['id']}",
            headers=admin_headers)
        assert resp.status_code == 400
