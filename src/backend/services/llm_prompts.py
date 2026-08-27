"""LLM prompt templates — strict JSON output contracts (SS-AI).

Pure functions returning {"system","user"} strings; consumed exclusively
by services/llm_pipeline.py. System prompts fix the examiner role and
forbid prose outside JSON so downstream parsing stays deterministic.
"""

_BASE_SYSTEM = (
    "You are an expert examiner for a technical learning platform. "
    "You reply with ONLY valid minified JSON matching the requested "
    "schema. No markdown fences, no commentary."
)


def skill_quiz_prompt(skill_name: str, difficulty: int, n: int,
                      avoid: list[str], proficiency_level: int = None,
                      topics: list[str] = None, locale: str = "en") -> dict:
    """Single-skill MCQ generation contract (practice tests).

    Dependencies: uses the module-level _BASE_SYSTEM examiner preamble.
    Implementation: builds a "user" string requesting n MCQs at the given
    difficulty, listing prior items to avoid (truncated to 20×80 chars). When
    proficiency_level is supplied the model targets that learner level (not a
    fixed hardness); when topics are supplied it focuses on them; locale
    selects the output language (Arabic for "ar", English otherwise). Returns a
    strict {"system","user"} JSON contract consumed by the pipeline; field
    names (text/options/correct_index) stay stable.
    """
    avoided = "; ".join(a[:80] for a in avoid[:20])
    target = ""
    if proficiency_level is not None:
        target = (f" Target the learner's current proficiency LEVEL "
                  f"{proficiency_level}/5 — calibrate question complexity to "
                  f"that level rather than the fixed difficulty scale.")
    focus = ""
    if topics:
        focus = " Focus specifically on these topics: " + "; ".join(
            str(t) for t in topics[:15]) + "."
    lang = " Arabic" if locale == "ar" else " English"
    user = (
        f'Write {n} multiple-choice questions about "{skill_name}" '
        f"(difficulty {difficulty}/5).{target}{focus} Avoid duplicating these "
        f'existing items: [{avoided}]. Write ALL generated text (questions, '
        f'options, explanations) in{lang}. '
        f'Schema: {{"questions":[{{"text":str,'
        f'"options":[str,str,str,str],"correct_index":0..3}}]}} '
        "Every question MUST contain exactly the keys text, options, "
        "correct_index; correct_index is the INTEGER 0..3 of the correct "
        "option. Example of one valid question: "
        '{"text":"Which runs Python code?","options":'
        '["CPython","GCC","JVM","LLVM"],"correct_index":0}'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def role_quiz_prompt(role_title: str, skills: list[dict],
                     proficiency_level: int = None,
                     topics: list[str] = None, locale: str = "en") -> dict:
    """Role-wide diagnostic quiz contract; each question tagged by skill.

    Dependencies: uses the module-level _BASE_SYSTEM preamble. Implementation:
    renders one row per skill (name + difficulty, defaulting to 1), asks for
    exactly 2 questions each tagged with the exact skill name, optionally
    focuses on topics and targets a learner level, and selects output language
    via locale; returns the strict {"system","user"} JSON contract for the
    pipeline to parse.
    """
    rows = "; ".join(
        f'{s["name"]} (difficulty {s.get("difficulty", 1)})' for s in skills)
    target = ""
    if proficiency_level is not None:
        target = (f" Target the learner's current proficiency LEVEL "
                  f"{proficiency_level}/5 when calibrating complexity.")
    focus = ""
    if topics:
        focus = " Focus specifically on these topics: " + "; ".join(
            str(t) for t in topics[:20]) + "."
    lang = " Arabic" if locale == "ar" else " English"
    user = (
        f'Diagnostic quiz for the job role "{role_title}". Skills: {rows}.{target}{focus} '
        f"For EACH listed skill write exactly 2 distinct questions. "
        f'Write ALL generated text (questions, options, explanations) in{lang}. '
        f'Schema: {{"questions":[{{"skill":exact-skill-name,"text":str,'
        f'"options":[str,str,str,str],"correct_index":0..3}}]}} '
        "Every question MUST contain exactly the keys skill, text, options, "
        "correct_index; correct_index is the INTEGER 0..3 of the correct "
        "option. Example of one valid question: "
        '{"skill":"JavaScript","text":"Which declares a constant?",'
        '"options":["let x","const x","var x","def x"],"correct_index":1}'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def diagnostic_analysis_prompt(per_skill: list[dict],
                                proficiency_level: int = None,
                                topics: list[str] = None,
                                locale: str = "en") -> dict:
    """Two-phase wizard analysis narrative contract (pre-path results).

    Dependencies: uses the module-level _BASE_SYSTEM preamble. Implementation:
    serializes one row per skill (correct/total, assessed_level, gap) and
    requests a strict summary/strengths/weaknesses/recommended_focus/next_steps
    schema; optionally focuses on topics and targets the learner level, and
    selects output language via locale; returns the {"system","user"} contract
    the pipeline caps and returns. Field names stay stable.
    """
    rows = "; ".join(
        f'{r["skill"]}: correct {r["correct"]}/{r["total"]}, '
        f'level {r["assessed_level"]}/5, gap {r["gap"]}' for r in per_skill)
    focus = ""
    if topics:
        focus = " Concentrate the recommendations on these topics: " + "; ".join(
            str(t) for t in topics[:20]) + "."
    lang = " Arabic" if locale == "ar" else " English"
    user = (
        f"Learner diagnostic results before path creation: {rows}.{focus} "
        f'Write ALL generated text (summary, notes, reasons, focus, '
        f'next_steps) in{lang}. '
        f'Schema: {{"summary":str,"strengths":[{{"skill":str,"note":str}}],'
        f'"weaknesses":[{{"skill":str,"reason":str,"focus":str}}],'
        f'"recommended_focus":[str],"next_steps":str}}'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def explain_result_prompt(responses: list[dict]) -> dict:
    """Per-question explanation + study advice contract.

    Dependencies: uses the module-level _BASE_SYSTEM preamble. Implementation:
    serializes each graded response (index, truncated question, selected/correct
    answer, is_correct) and requests a strict explanations[question_index,why] +
    advice schema covering every index; returns the {"system","user"} contract.
    """
    rows = "; ".join(
        f'#{r["question_index"]} "{r["question"][:70]}" '
        f'selected={r["selected_index"]} correct='
        f'{r["correct_answer"]!r} right={r["is_correct"]}'
        for r in responses)
    user = (
        f"Explain this graded attempt. Rows: {rows}. "
        f'Schema: {{"explanations":[{{"question_index":int,"why":str}}],'
        f'"advice":str}} — cover EVERY question_index.'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def skill_topics_prompt(skill_name: str, level: int, n: int) -> dict:
    """Level-appropriate practice-topic contract for a single skill.

    Dependencies: uses the module-level _BASE_SYSTEM preamble. Implementation:
    requests exactly n concise practice topics tuned to the given learner
    LEVEL (1..5) so higher levels surface deeper/subtopic material; returns the
    strict {"system","user"} {"topics":[str,...]} contract the pipeline parses.
    """
    user = (
        f'List {n} distinct practice topics for learning "{skill_name}" '
        f"appropriate for a learner at LEVEL {level}/5 (deeper, more specific "
        f"topics as the level rises). "
        f'Schema: {{"topics":[str]}} — return ONLY the JSON object, no prose.'
    )
    return {"system": _BASE_SYSTEM, "user": user}


def review_level_prompt(correct: int, total: int, difficulty: int,
                        attempt_no: int, current_level: int) -> dict:
    """Bounded proficiency-review contract (±1 delta, confidence-gated).

    Dependencies: uses the module-level _BASE_SYSTEM preamble. Implementation:
    states the score/difficulty/attempt/level, the round(score/total*5) formula,
    and asks the model to judge misrepresentation, returning a strict
    {"suggested_delta":-1|0|1,"confidence","rationale<=300"} contract the
    pipeline coerces into safe ranges before applying any delta.
    """
    user = (
        f"A learner scored {correct}/{total} on a difficulty-{difficulty} "
        f"quiz (attempt #{attempt_no}); stored level is {current_level}/5 "
        f"(formula level = round({correct}/{total}*5)). Judge whether the "
        "raw score misrepresents mastery (guessing, near-miss patterns). "
        'Schema: {"suggested_delta":-1|0|1,"confidence":"high"|"medium"|"low",'
        '"rationale":str<=300}. Use high confidence ONLY for clear evidence.'
    )
    return {"system": _BASE_SYSTEM, "user": user}
