"""tests/test_llm_pipeline.py — per-skill role quiz generation (SS-AI)."""
import pytest

from backend.services import llm_pipeline as pipe


def _enable_engine(monkeypatch):
    """Force the pipeline gate open without a real model."""
    from backend.services import llm_engine
    monkeypatch.setattr(llm_engine, "available", lambda: True)


def test_generate_role_quiz_merges_tagged(monkeypatch):
    """Each skill's questions are tagged with the exact skill name."""
    _enable_engine(monkeypatch)

    def fake(name, *a, **k):
        if name == "Python":
            return [{"text": "p1", "options": ["a", "b", "c", "d"],
                     "correct_index": 0}]
        if name == "SQL":
            return [{"text": "s1", "options": ["a", "b", "c", "d"],
                     "correct_index": 2}]
        return []

    monkeypatch.setattr(pipe, "generate_skill_quiz", fake)
    skills = [{"name": "Python", "difficulty": 2, "topics": []},
              {"name": "SQL", "difficulty": 1, "topics": []}]
    out = pipe.generate_role_quiz("Backend", skills)
    assert [q["skill"] for q in out] == ["Python", "SQL"]
    assert out[0]["text"] == "p1" and out[0]["correct_index"] == 0
    assert out[1]["text"] == "s1" and out[1]["correct_index"] == 2


def test_generate_role_quiz_skips_failed_skill(monkeypatch):
    """A single failing skill is skipped, the rest still merge."""
    _enable_engine(monkeypatch)

    def fake(name, *a, **k):
        if name == "Bad":
            raise pipe.LLMOperationError("boom")
        return [{"text": "g1", "options": ["a", "b", "c", "d"],
                 "correct_index": 0}]

    monkeypatch.setattr(pipe, "generate_skill_quiz", fake)
    out = pipe.generate_role_quiz("R", [{"name": "Good"}, {"name": "Bad"}])
    assert [q["skill"] for q in out] == ["Good"]


def test_generate_role_quiz_empty_raises(monkeypatch):
    """No surviving questions surfaces LLMOperationError."""
    _enable_engine(monkeypatch)
    monkeypatch.setattr(pipe, "generate_skill_quiz", lambda *a, **k: [])
    with pytest.raises(pipe.LLMOperationError):
        pipe.generate_role_quiz("R", [{"name": "X"}])


def test_generate_role_quiz_streams_on_skill(monkeypatch):
    """The on_skill hook fires per skill with the merged chunk."""
    _enable_engine(monkeypatch)
    monkeypatch.setattr(pipe, "generate_skill_quiz",
                        lambda name, *a, **k: [
                            {"text": f"{name} q", "options": ["a", "b", "c", "d"],
                             "correct_index": 0}])
    seen = []
    pipe.generate_role_quiz(
        "R", [{"name": "A"}, {"name": "B"}], on_skill=lambda n, c: seen.append(n))
    assert seen == ["A", "B"]
