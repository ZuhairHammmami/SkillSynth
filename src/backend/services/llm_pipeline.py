"""LLM pipeline — validated high-level operations over llm_engine (SS-AI).

Sole consumer of services/llm_engine.complete and llm_prompts templates;
called by routers/ai.py and the assess-service review hook. Every op
first gates on _engine_available() so a present-but-unusable engine
degrades gracefully, then either returns contract-valid data or a
documented fallback (None / raise) per spec Failure Handling.
"""
import json
import logging
import re

from backend.services import llm_prompts as prompts

logger = logging.getLogger(__name__)

_CONFIDENCES = ("high", "medium", "low")


class LLMOperationError(Exception):
    """Engine unavailable or all retries exhausted / output invalid."""


def _engine_available() -> bool:
    """Report engine readiness; test seam monkeypatched to bypass engine.

    Called by every public op as its first gate; delegates to
    llm_engine.available() in production.
    """
    from backend.services import llm_engine
    return llm_engine.available()


def _engine_factory():
    """Return the engine provider; test seam monkeypatched by tests.

    Called by _complete_json only; returns the llm_engine module whose
    complete() performs inference.
    """
    from backend.services import llm_engine
    return llm_engine


def _extract_json(text: str) -> dict:
    """Parse the first {...} block from a raw completion string.

    Called by _complete_json on each attempt; raises ValueError when no
    object exists and json.JSONDecodeError on malformed content so the
    caller records the error and retries.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found")
    return json.loads(match.group(0))


def _complete_json(contract: dict, *, max_tokens: int) -> dict:
    """Complete a prompts-template contract with ONE corrective retry.

    Shared callee of all five public ops; reads contract["system"] /
    ["user"], appends the parse error to the retry turn, then raises
    LLMOperationError once both attempts fail.
    """
    engine = _engine_factory()
    last_err = ""
    for _ in range(2):
        suffix = "" if not last_err else (
            f"\nYour previous reply was invalid JSON ({last_err}). "
            "Reply again with ONLY the JSON object.")
        try:
            raw = engine.complete(
                contract["system"] + "\n\n" + contract["user"] + suffix,
                max_tokens=max_tokens)
            return _extract_json(raw)
        except (ValueError, json.JSONDecodeError) as exc:
            last_err = str(exc)[:120]
    raise LLMOperationError(f"invalid JSON after retry: {last_err}")


def sanitize_topic(text: str, limit: int = 120) -> str:
    """Strip braces/backticks/control chars; clamp length.

    Applied by generate_skill_quiz / generate_role_quiz to skill names
    and role titles before they reach prompts (injection hardening).
    """
    cleaned = re.sub(r"[{}<>`\\]|[\x00-\x1f]", "", str(text))
    return cleaned.strip()[:limit]


def _valid_question(q, seen_texts: set[str], exclude_texts: set[str]) -> bool:
    """Schema gate for one MCQ; True iff usable.

    Callee of generate_skill_quiz / generate_role_quiz; enforces 4
    non-empty string options, correct_index 0..3, fresh non-excluded text.
    """
    if not isinstance(q, dict):
        return False
    text, opts = q.get("text"), q.get("options")
    idx = q.get("correct_index")
    return (isinstance(text, str) and text.strip()
            and isinstance(opts, list) and len(opts) == 4
            and all(isinstance(o, str) and o.strip() for o in opts)
            and isinstance(idx, int) and 0 <= idx <= 3
            and text.strip() not in seen_texts
            and text.strip() not in exclude_texts)


def generate_skill_quiz(skill_name: str, difficulty: int, n: int = 5,
                        exclude_texts=frozenset()) -> list[dict]:
    """Validated single-skill MCQs for practice tests.

    Called by routers/ai.py; gates on _engine_available() (raise "AI
    unavailable"), validates via _valid_question, raises
    LLMOperationError when nothing survives so callers fall back to
    seeded quizzes.
    """
    if not _engine_available():
        raise LLMOperationError("AI unavailable")
    topic = sanitize_topic(skill_name)
    exclude = set(exclude_texts)
    data = _complete_json(
        prompts.skill_quiz_prompt(topic, difficulty, n, sorted(exclude)),
        max_tokens=max(400, n * 140))
    out: list[dict] = []
    for q in data.get("questions", []):
        if _valid_question(q, {x["text"] for x in out}, exclude):
            out.append({"text": q["text"].strip(),
                        "options": [o.strip() for o in q["options"]],
                        "correct_index": q["correct_index"]})
    if not out:
        raise LLMOperationError("no valid questions returned")
    return out


def generate_role_quiz(role_title: str, skills: list[dict],
                       exclude_texts=frozenset()) -> list[dict]:
    """Validated role diagnostic quiz; items carry exact skill tag.

    Called by routers/ai.py; gates on _engine_available() (raise "AI
    unavailable"), keeps only questions tagged with a requested skill
    name that pass _valid_question; per-skill shortfall is tolerated
    downstream (analysis handles partial coverage).
    """
    if not _engine_available():
        raise LLMOperationError("AI unavailable")
    safe = [{"name": sanitize_topic(s["name"]),
             "difficulty": int(s.get("difficulty") or 1)} for s in skills]
    data = _complete_json(
        prompts.role_quiz_prompt(sanitize_topic(role_title), safe),
        max_tokens=max(600, len(safe) * 280))
    exclude, out = set(exclude_texts), []
    seen_names = {s["name"] for s in safe}
    for q in data.get("questions", []):
        if q.get("skill") not in seen_names:
            continue
        base = {k: q[k] for k in ("text", "options", "correct_index")}
        if _valid_question(base, {x["text"] for x in out}, exclude):
            out.append({**base, "skill": q["skill"],
                        "text": base["text"].strip()})
    if not out:
        raise LLMOperationError("no valid role-quiz questions")
    return out


def analyze_diagnostic(per_skill: list[dict]) -> dict | None:
    """Narrative report for pre-path results; None ⇒ deterministic fallback.

    Called by routers/ai.py wizard analysis; gates on _engine_available()
    (return None), caps narrative fields to bounded sizes, and converts
    any failure into None so callers render the numbers-only report.
    """
    if not _engine_available():
        logger.info("analyze_diagnostic skipped: AI unavailable")
        return None
    try:
        data = _complete_json(
            prompts.diagnostic_analysis_prompt(per_skill), max_tokens=500)
        return {
            "summary": str(data.get("summary", ""))[:800],
            "strengths": data.get("strengths", [])[:8],
            "weaknesses": data.get("weaknesses", [])[:8],
            "recommended_focus": [str(x) for x in
                                  data.get("recommended_focus", [])][:5],
            "next_steps": str(data.get("next_steps", ""))[:400],
        }
    except Exception as exc:  # noqa: BLE001 — documented None fallback
        logger.warning("analyze_diagnostic fallback: %s", exc)
        return None


def explain_result(responses: list[dict]) -> dict | None:
    """Per-question explanations + advice; None ⇒ static recap fallback.

    Called by routers/ai.py result explanation endpoint; gates on
    _engine_available() (return None), keeps only explanations whose
    question_index matches a graded row, and converts any failure into
    None.
    """
    if not _engine_available():
        logger.info("explain_result skipped: AI unavailable")
        return None
    try:
        data = _complete_json(
            prompts.explain_result_prompt(responses), max_tokens=650)
        known = {r["question_index"] for r in responses}
        expl = [{"question_index": e.get("question_index"),
                 "why": str(e.get("why", ""))[:400]}
                for e in data.get("explanations", [])
                if e.get("question_index") in known]
        return {"explanations": expl,
                "advice": str(data.get("advice", ""))[:500]}
    except Exception as exc:  # noqa: BLE001 — documented None fallback
        logger.warning("explain_result fallback: %s", exc)
        return None


def review_level(correct: int, total: int, difficulty: int,
                 attempt_no: int, current_level: int) -> dict:
    """Bounded-autonomy level verdict; never moves beyond ±1/high-conf.

    Called by the assess-service review hook after each quiz attempt;
    gates on _engine_available() (delta-0/low-confidence fallback),
    coerces model output into safe ranges, and applies the delta only
    when confidence is high, delta non-zero, and target stays 0..5.
    The reported delta keeps the suggestion when confidence is high even
    if clamping blocked application (applied=False, final=current).
    """
    if not _engine_available():
        return {"delta": 0, "confidence": "low",
                "rationale": "AI unavailable", "applied": False,
                "final_level": max(0, min(5, current_level))}
    try:
        data = _complete_json(
            prompts.review_level_prompt(correct, total, difficulty,
                                        attempt_no, current_level),
            max_tokens=220)
        delta = data.get("suggested_delta")
        conf = data.get("confidence")
        if not (isinstance(delta, int) and -1 <= delta <= 1):
            delta = 0
        conf = conf if conf in _CONFIDENCES else "low"
        rationale = str(data.get("rationale", ""))[:300]
    except Exception as exc:  # noqa: BLE001 — documented safe fallback
        logger.warning("review_level fallback: %s", exc)
        delta, conf, rationale = 0, "low", f"review unavailable: {exc}"
    effective = delta if conf == "high" else 0
    target = current_level + effective
    applied = conf == "high" and effective != 0 and 0 <= target <= 5
    final = target if applied else current_level
    return {"delta": effective, "confidence": conf, "rationale": rationale,
            "applied": applied, "final_level": max(0, min(5, final))}
