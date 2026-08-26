"""tests/test_llm_prompts.py — JSON contract markers present."""
from backend.services import llm_prompts as P


def test_skill_quiz_contract():
    """Quiz prompt pins option-count/index-range JSON shape.

    Consumed by pipeline.generate_skill_quiz validation.
    """
    p = P.skill_quiz_prompt("React Hooks", 2, 3, ["old text"])
    assert '"questions"' in p["user"] and '"correct_index"' in p["user"]
    assert "React Hooks" in p["user"] and "old text" in p["user"]


def test_quiz_prompts_pin_keys_with_exemplar():
    """Both quiz prompts state exact key rule + one-shot exemplar.

    Guards against the 3B model omitting correct_index / fragmenting
    question objects (task-13 follow-up).
    """
    skill_p = P.skill_quiz_prompt("Python Basics", 1, 2, [])
    role_p = P.role_quiz_prompt(
        "Frontend Developer", [{"name": "JavaScript", "difficulty": 2}])
    for p in (skill_p, role_p):
        assert "correct_index" in p["user"] and "Example" in p["user"]
        assert "INTEGER 0..3" in p["user"]
    assert '"skill"' in role_p["user"]


def test_role_quiz_tags_skills():
    """Role prompt requires a skill tag per question.

    Keeps wizard ids round-tripping into learning_service._score_answers.
    """
    p = P.role_quiz_prompt("Frontend Developer",
                           [{"name": "JavaScript", "difficulty": 2}])
    assert '"skill"' in p["user"] and "JavaScript" in p["user"]


def test_review_delta_enum():
    """Review prompt constrains delta/confidence enums exactly.

    Consumed by pipeline.review_level bounded-autonomy policy.
    """
    p = P.review_level_prompt(7, 10, 3, 2, 2)
    assert '"suggested_delta"' in p["user"] and '"high"' in p["user"]
    assert "-1" in p["user"] and "1" in p["user"]
