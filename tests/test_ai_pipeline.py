"""tests/test_ai_pipeline.py — pipeline ops against a fake engine."""
import json

import pytest

from backend.services import llm_pipeline as pipe


class FakeEngine:
    """Scriptable stand-in for llm_engine.complete.

    Returns queued payloads regardless of prompt; records calls.
    """
    def __init__(self, payloads):
        self.queue = list(payloads)
        self.calls = []

    def complete(self, prompt, *, max_tokens, temperature=None):
        self.calls.append(prompt)
        item = self.queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item if isinstance(item, str) else json.dumps(item)


@pytest.fixture
def fake(monkeypatch):
    """Install a FakeEngine factory as pipe._engine_factory."""
    holder = {}

    def install(*payloads):
        eng = FakeEngine(list(payloads))
        monkeypatch.setattr(pipe, "_engine_factory", lambda: eng)
        holder["eng"] = eng
        return eng

    monkeypatch.setattr(pipe, "_engine_available", lambda: True)
    return install


def test_skill_quiz_happy(fake):
    """Valid model JSON validates into clean question dicts."""
    fake({"questions": [
        {"text": f"Q{i}", "options": ["a", "b", "c", "d"],
         "correct_index": i % 4} for i in range(3)]})
    qs = pipe.generate_skill_quiz("SQL", 2, 3)
    assert len(qs) == 3 and qs[0]["options"][qs[0]["correct_index"]] == "a"


def test_retry_then_error(fake):
    """Bad JSON retries once with an error hint, then raises."""
    eng = fake("not json at all", {"questions": []})
    with pytest.raises(pipe.LLMOperationError):
        pipe.generate_skill_quiz("SQL", 2, 1)
    assert len(eng.calls) == 2 and "invalid" in eng.calls[1].lower()


def test_question_validation_filters(fake):
    """Wrong arity/options/index/duplicates get dropped, not crash."""
    fake({"questions": [
        {"text": "ok", "options": ["a", "b", "c", "d"], "correct_index": 0},
        {"text": "bad-arity", "options": ["a", "b"], "correct_index": 0},
        {"text": "bad-index", "options": ["a", "b", "c", "d"],
         "correct_index": 9},
        {"text": "ok-dup", "options": ["a", "b", "c", "d"],
         "correct_index": 1},
        {"text": "ok", "options": ["w", "x", "y", "z"], "correct_index": 2},
    ]})
    qs = pipe.generate_skill_quiz("Git", 1, 5, exclude_texts={"ok"})
    assert [q["text"] for q in qs] == ["ok-dup"]


def test_review_bounded_policy(fake):
    """Medium confidence forces delta 0; high respects clamp range."""
    fake({"suggested_delta": 1, "confidence": "medium", "rationale": "r"})
    out = pipe.review_level(7, 10, 2, 1, 2)
    assert out["delta"] == 0 and out["applied"] is False
    fake({"suggested_delta": 1, "confidence": "high", "rationale": "sure"})
    up = pipe.review_level(9, 10, 2, 1, 4)
    assert up["delta"] == 1 and up["applied"] and up["final_level"] == 5
    fake({"suggested_delta": -1, "confidence": "high", "rationale": "sure"})
    dn = pipe.review_level(0, 10, 2, 1, 0)
    assert dn["delta"] == -1 and dn["applied"] is False and \
        dn["final_level"] == 0


def test_analyze_fallback_none(fake):
    """Engine blow-up yields None so callers fall back deterministically."""
    fake(RuntimeError("boom"))
    assert pipe.analyze_diagnostic(
        [{"skill": "X", "correct": 1, "total": 2, "assessed_level": 1,
          "gap": 2}]) is None
