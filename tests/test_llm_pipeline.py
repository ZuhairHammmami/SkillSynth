"""tests/test_llm_pipeline.py — per-skill role quiz generation (SS-AI)."""
import pytest

from backend.services import llm_pipeline as pipe


def _enable_engine(monkeypatch):
    """Force the pipeline gate open without a real model."""
    from backend.services import llm_engine
    monkeypatch.setattr(llm_engine, "available", lambda: True)


def _batch(questions):
    """A fake _complete_json returning a batched {"questions": [...]} dict."""
    return lambda contract, **k: {"questions": questions}


def _q(skill, text, ci=0):
    return {"skill": skill, "text": text,
            "options": ["a", "b", "c", "d"], "correct_index": ci}


def test_generate_role_quiz_merges_tagged(monkeypatch):
    """Each skill's questions are tagged with its exact skill name (batched)."""
    _enable_engine(monkeypatch)
    monkeypatch.setattr(
        pipe, "_complete_json",
        _batch([_q("Python", "p1", 0), _q("SQL", "s1", 2)]))
    skills = [{"name": "Python", "difficulty": 2, "topics": []},
              {"name": "SQL", "difficulty": 1, "topics": []}]
    out = pipe.generate_role_quiz("Backend", skills)
    assert [q["skill"] for q in out] == ["Python", "SQL"]
    assert out[0]["text"] == "p1" and out[0]["correct_index"] == 0
    assert out[1]["text"] == "s1" and out[1]["correct_index"] == 2


def test_generate_role_quiz_skips_failed_skill(monkeypatch):
    """A failing (empty-batch) skill is skipped; the rest still merge."""
    _enable_engine(monkeypatch)
    monkeypatch.setattr(pipe, "_complete_json", _batch([]))

    def fake_generate_skill_quiz(name, *a, **k):
        if name == "Bad":
            raise pipe.LLMOperationError("boom")
        return [{"text": "g1", "options": ["a", "b", "c", "d"],
                 "correct_index": 0}]

    monkeypatch.setattr(pipe, "generate_skill_quiz", fake_generate_skill_quiz)
    out = pipe.generate_role_quiz("R", [{"name": "Good"}, {"name": "Bad"}])
    assert [q["skill"] for q in out] == ["Good"]


def test_generate_role_quiz_empty_raises(monkeypatch):
    """No surviving questions surfaces LLMOperationError."""
    _enable_engine(monkeypatch)
    monkeypatch.setattr(pipe, "_complete_json", _batch([]))
    monkeypatch.setattr(pipe, "generate_skill_quiz", lambda *a, **k: [])
    with pytest.raises(pipe.LLMOperationError):
        pipe.generate_role_quiz("R", [{"name": "X"}])


def test_generate_role_quiz_streams_on_skill(monkeypatch):
    """The on_skill hook fires per skill in order with the batched chunk."""
    _enable_engine(monkeypatch)
    monkeypatch.setattr(
        pipe, "_complete_json",
        _batch([_q("A", "a q"), _q("B", "b q")]))
    seen = []
    pipe.generate_role_quiz(
        "R", [{"name": "A"}, {"name": "B"}], on_skill=lambda n, c: seen.append(n))
    assert seen == ["A", "B"]


def test_generate_role_quiz_batches_skills(monkeypatch):
    """A role of many skills runs fewer completions than skills (batched)."""
    _enable_engine(monkeypatch)
    all_qs = [_q(f"S{i}", f"q{i}", 0) for i in range(9)]
    calls = []

    def fake_complete(contract, **k):
        calls.append(k)
        return {"questions": all_qs}

    monkeypatch.setattr(pipe, "_complete_json", fake_complete)
    skills = [{"name": f"S{i}"} for i in range(9)]
    pipe.generate_role_quiz("R", skills)
    assert len(calls) == 3  # ceil(9 / 4 per batch) = 3 completions, not 9


def test_generate_skill_quiz_trims_max_tokens(monkeypatch):
    """Skill quiz max_tokens ceiling is trimmed (no longer 650 for n<=2)."""
    captured = {}

    def fake_complete(contract, **k):
        captured["max_tokens"] = k["max_tokens"]
        return {"questions": [{"text": "q1", "options": ["a", "b", "c", "d"],
                               "correct_index": 0}]}

    monkeypatch.setattr(pipe, "_engine_available", lambda: True)
    monkeypatch.setattr(pipe, "_complete_json", fake_complete)
    pipe.generate_skill_quiz("Python", 2, n=2)
    assert captured["max_tokens"] <= 220  # min(700, max(180, 2*95))=190


def test_analyze_diagnostic_trims_max_tokens(monkeypatch):
    """Wizard-analysis narrative max_tokens is trimmed to 400."""
    captured = {}

    def fake_complete(contract, **k):
        captured["max_tokens"] = k["max_tokens"]
        return {"summary": "s", "strengths": [], "weaknesses": [],
                "recommended_focus": [], "next_steps": ""}

    monkeypatch.setattr(pipe, "_engine_available", lambda: True)
    monkeypatch.setattr(pipe, "_complete_json", fake_complete)
    pipe.analyze_diagnostic([{"skill": "X", "correct": 1, "total": 2,
                              "assessed_level": 2, "gap": 1}])
    assert captured["max_tokens"] == 400


def test_generate_skill_quiz_threads_context(monkeypatch):
    """A supplied context block is injected into the generated prompt."""
    captured = {}

    def fake_complete(contract, **k):
        captured["user"] = contract["user"]
        return {"questions": [{"text": "q1", "options": ["a", "b", "c", "d"],
                               "correct_index": 0}]}

    monkeypatch.setattr(pipe, "_engine_available", lambda: True)
    monkeypatch.setattr(pipe, "_complete_json", fake_complete)
    out = pipe.generate_skill_quiz(
        "Python", 2, n=1,
        context="Project reference for this skill:\n- Description: scripting")
    assert out[0]["text"] == "q1"
    assert "Project reference for this skill:" in captured["user"]


def test_generate_skill_quiz_no_context_unchanged(monkeypatch):
    """Absent context leaves the prompt identical to the pre-grounding form."""
    captured = {}

    def fake_complete(contract, **k):
        captured["user"] = contract["user"]
        return {"questions": [{"text": "q1", "options": ["a", "b", "c", "d"],
                               "correct_index": 0}]}

    monkeypatch.setattr(pipe, "_engine_available", lambda: True)
    monkeypatch.setattr(pipe, "_complete_json", fake_complete)
    pipe.generate_skill_quiz("Python", 2, n=1)
    assert "Project reference for this skill:" not in captured["user"]


def test_complete_json_forwards_grammar_flag(monkeypatch):
    """_complete_json forwards a grammar string only when AI_GRAMMAR is on."""
    calls = {}

    class FakeEngine:
        @staticmethod
        def complete(prompt, **k):
            calls["grammar"] = k.get("grammar")
            return '{"x":1}'

    monkeypatch.setattr(pipe, "_engine_factory", lambda: FakeEngine)
    from backend.config import app_settings as settings
    monkeypatch.setattr(settings, "AI_GRAMMAR", True)
    pipe._complete_json({"system": "s", "user": "u"}, max_tokens=10,
                        grammar="root ::= ...")
    assert calls["grammar"] is not None
    monkeypatch.setattr(settings, "AI_GRAMMAR", False)
    pipe._complete_json({"system": "s", "user": "u"}, max_tokens=10,
                        grammar="root ::= ...")
    assert calls["grammar"] is None
