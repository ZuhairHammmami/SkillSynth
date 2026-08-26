"""tests/test_ai_repo.py — AI assessment persistence helper."""
import pytest

from backend.entities.assessment import Assessment, AssessmentQuestion
from backend.repositories import assess_repository as arepo


@pytest.fixture(autouse=True)
def purge_ai_rows(db_session):
    """Delete [AI]-titled assessments after each test so later suites see
    exact seed counts (test_schema.py pins eight table totals; mirrors
    integrity_support.teardown contract)."""
    yield
    ai_ids = db_session.query(Assessment.id).filter(
        Assessment.title.like("[AI]%"))
    db_session.query(AssessmentQuestion).filter(
        AssessmentQuestion.assessment_id.in_(ai_ids)).delete(
        synchronize_session=False)
    db_session.query(Assessment).filter(
        Assessment.title.like("[AI]%")).delete(synchronize_session=False)
    db_session.commit()


def _questions(n):
    """Build n valid MCQ dicts for create_assessment_with_questions.

    Used by this module's tests only.
    """
    return [{"text": f"Q{i}?", "options": ["a", "b", "c", "d"],
             "correct_index": i % 4} for i in range(n)]


def test_create_assessment_with_questions(db_session):
    """Created row carries title/pass_score and ordered questions.

    Consumed by routers/ai.py practice-test flow (Task 6); mirrors the
    mk_assessment pattern from integrity_support.
    """
    a = arepo.create_assessment_with_questions(
        db_session, None, "[AI] Demo — adaptive", "ss-ai:v1", 60,
        _questions(3))
    assert a.id is not None and a.title.startswith("[AI]")
    qs = arepo.get_questions(db_session, a.id)
    assert [q.prompt for q in qs] == ["Q0?", "Q1?", "Q2?"]
    assert qs[1].position == 2 and qs[1].correct_index == 1
