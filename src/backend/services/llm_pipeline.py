"""LLM pipeline — validated ops over llm_engine (SS-AI). Sole consumer of llm_engine.complete and llm_prompts templates; called by routers/ai.py and the assess review hook. Each op gates on _engine_available() and degrades gracefully; _extract_json is the strict parse and _salvage_* recover sub-objects from broken output."""
import json
import logging
import re
from typing import Callable

from backend.config import app_settings as settings
from backend.services import llm_prompts as prompts
from backend.services import settings_service

logger = logging.getLogger(__name__)

_CONFIDENCES = ("high", "medium", "low")


class LLMOperationError(Exception):
    """Engine unavailable or all retries exhausted / output invalid."""


def _engine_available() -> bool:
    """First gate of every public op. Deps: imports backend.services.llm_engine and calls its available(). Impl: thin wrapper so tests monkeypatch the gate."""
    from backend.services import llm_engine
    return llm_engine.available()


def _engine_factory():
    """Return the engine provider module for inference. Deps: imports backend.services.llm_engine. Impl: returns the module whose complete() runs inference; the indirection is a test seam."""
    from backend.services import llm_engine
    return llm_engine


def _extract_json(text: str) -> dict:
    """Parse the FIRST JSON object, ignoring chatter. Deps: json.JSONDecoder().raw_decode. Impl: scans to first "{" and decodes one object, raising ValueError when none parses so the caller retries."""
    idx = text.find("{")
    if idx == -1:
        raise ValueError("no JSON object found")
    obj, _ = json.JSONDecoder().raw_decode(text[idx:])
    return obj


def _iter_objects(text: str) -> list[dict]:
    """Yield every balanced {...} substring decoded as a dict. Deps: json.loads per brace pair. Impl: stack scan recovers objects the model emitted concatenated/wrapped/nested in a malformed outer doc; braces in strings are rare (backticks used instead)."""
    objs: list[dict] = []
    stack: list[int] = []
    for i, ch in enumerate(text):
        if ch == "{":
            stack.append(i)
        elif ch == "}" and stack:
            start = stack.pop()
            try:
                objs.append(json.loads(text[start:i + 1]))
            except Exception:  # noqa: BLE001 — skip non-JSON fragments
                pass
    return objs


def _salvage_questions(text: str) -> dict | None:
    """Recover valid MCQs from broken quiz output. Deps: _iter_objects, _valid_question. Impl: scans each balanced object and nested lists for dicts passing _valid_question, returning {"questions":[...]} or None."""
    out: list[dict] = []

    def consider(q):
        if not isinstance(q, dict):
            return
        if _valid_question(q, {x["text"] for x in out}, set()):
            item = {"text": q["text"].strip(),
                    "options": [o.strip() for o in q["options"]],
                    "correct_index": q["correct_index"]}
            if q.get("skill"):
                item["skill"] = q["skill"]
            out.append(item)

    for obj in _iter_objects(text):
        if not isinstance(obj, dict):
            continue
        consider(obj)
        for value in obj.values():
            if isinstance(value, list):
                for item in value:
                    consider(item)
    return {"questions": out} if out else None


def _salvage_diagnostic(text: str) -> dict | None:
    """Recover the narrative report from broken diagnostic output. Deps: _iter_objects. Impl: returns the object carrying the most diagnostic keys (summary/strengths/weaknesses/recommended_focus/next_steps), else None."""
    keys = ("summary", "strengths", "weaknesses",
            "recommended_focus", "next_steps")
    best = None
    best_score = 0
    for obj in _iter_objects(text):
        if isinstance(obj, dict):
            score = sum(k in obj for k in keys)
            if score > best_score:
                best, best_score = obj, score
    return best


def _salvage_explanations(text: str) -> dict | None:
    """Recover the explanation list from broken explain output. Deps: _iter_objects. Impl: prefers a {"explanations":[...]} wrapper; else gathers {"question_index":int,"why":str} objects (wrapper items skipped to avoid double-count). Returns {"explanations":[...]} or None."""
    objs = _iter_objects(text)
    for obj in objs:
        if (isinstance(obj, dict) and "explanations" in obj
                and isinstance(obj["explanations"], list)):
            expls = [e for e in obj["explanations"]
                     if isinstance(e, dict) and "question_index" in e]
            if expls:
                return {"explanations": expls}
    expls = [obj for obj in objs
             if isinstance(obj, dict) and "question_index" in obj
             and "why" in obj and "explanations" not in obj]
    return {"explanations": expls} if expls else None


def _complete_json(contract: dict, *, max_tokens: int,
                   temperature: float | None = None,
                   salvage: Callable[[str], dict | None] | None = None) -> dict:
    """Complete a prompts contract with ONE corrective retry. Deps: _engine_factory().complete, _extract_json, optional salvage hook. Impl: reads contract system/user, appends prior parse error to a retry turn, forwards a temperature override; on failure offers raw payload to salvage, else raises LLMOperationError."""
    engine = _engine_factory()
    last_err = ""
    raw = None
    for _ in range(2):
        suffix = "" if not last_err else (
            f"\nYour previous reply was invalid JSON ({last_err}). "
            "Reply again with ONLY the JSON object. "
            "Every question object requires text, options (exactly 4 "
            "strings) and correct_index.")
        try:
            raw = engine.complete(
                contract["system"] + "\n\n" + contract["user"] + suffix,
                max_tokens=max_tokens, temperature=temperature)
            return _extract_json(raw)
        except (ValueError, json.JSONDecodeError) as exc:
            last_err = str(exc)[:120]
    if salvage is not None and raw is not None:
        salvaged = salvage(raw)
        if salvaged is not None:
            return salvaged
    raise LLMOperationError(f"invalid JSON after retry: {last_err}")


def sanitize_topic(text: str, limit: int = 120) -> str:
    """Strip braces/backticks/control chars; clamp length. Deps: re.sub. Impl: removes {,},<,>,`,\\ and control chars, trims, clamps to `limit`; used on skill/role names before prompts (injection hardening)."""
    cleaned = re.sub(r"[{}<>`\\]|[\x00-\x1f]", "", str(text))
    return cleaned.strip()[:limit]


def _valid_question(q, seen_texts: set[str], exclude_texts: set[str]) -> bool:
    """Schema gate for one MCQ; True iff usable. Deps: builtins only. Impl: enforces 4 non-empty string options, correct_index 0..3, and a fresh text not in seen_texts or exclude_texts."""
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


def _salvage_topics(text: str) -> dict | None:
    """Recover a topics list from broken topic output. Deps: _iter_objects. Impl: returns the first balanced object carrying a non-empty "topics" list, else None."""
    for obj in _iter_objects(text):
        if isinstance(obj, dict) and isinstance(obj.get("topics"), list):
            return obj
    return None


def generate_skill_topics(skill_name: str, level: int) -> list[str]:
    """Level-appropriate practice topics for a skill, or seeded fallback. Deps: settings_service.is_ai_enabled, _engine_available, prompts.skill_topics_prompt, _complete_json, _salvage_topics. Impl: when AI is enabled at runtime and the engine is ready asks for min(3, level+1) topics, else returns a deterministic seeded fallback so callers/tests never require the LLM."""
    if not (settings_service.is_ai_enabled() and _engine_available()):
        return _seeded_topics(skill_name, level)
    try:
        data = _complete_json(
            prompts.skill_topics_prompt(
                sanitize_topic(skill_name), level, min(3, level + 1)),
            max_tokens=400, salvage=_salvage_topics)
        topics = [str(t) for t in data.get("topics", []) if str(t).strip()]
        if topics:
            return topics[: min(3, level + 1)]
    except LLMOperationError:
        pass
    return _seeded_topics(skill_name, level)


def _seeded_topics(skill_name: str, level: int) -> list[str]:
    """Deterministic fallback topic list for a skill at a level. Deps: builtins. Impl: produces min(3, level+1) reproducible strings so tests need no LLM."""
    return [f"Topic {i} for {skill_name} (level {level})"
            for i in range(1, min(3, level + 1) + 1)]


def generate_skill_quiz(skill_name: str, difficulty: int, n: int = 5,
                         exclude_texts=frozenset(),
                         proficiency_level: int = None,
                         topics: list = None, locale: str = "en") -> list[dict]:
    """Validated single-skill MCQs for practice tests. Deps: _engine_available, sanitize_topic, prompts.skill_quiz_prompt, _complete_json, _valid_question. Impl: gates on engine (raise "AI unavailable"), validates output, raises LLMOperationError when nothing survives so callers fall back to seeded quizzes. New optional params target the learner level, focus on topics, and select output locale."""
    if not _engine_available():
        raise LLMOperationError("AI unavailable")
    topic = sanitize_topic(skill_name)
    exclude = set(exclude_texts)
    data = _complete_json(
        prompts.skill_quiz_prompt(
            topic, difficulty, n, sorted(exclude),
            proficiency_level=proficiency_level,
            topics=[sanitize_topic(t) for t in topics] if topics else None,
            locale=locale),
        max_tokens=max(650, n * 230),
        salvage=_salvage_questions)
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
                        exclude_texts=frozenset(),
                        proficiency_level: int = None,
                        topics: list = None, locale: str = "en") -> list[dict]:
    """Validated role diagnostic quiz; items carry exact skill tag. Deps: _engine_available, sanitize_topic, prompts.role_quiz_prompt, _complete_json, _valid_question. Impl: gates on engine, keeps only questions tagged with a requested skill passing _valid_question; per-skill shortfall tolerated downstream. New optional params target the learner level, focus on topics, and select output locale."""
    if not _engine_available():
        raise LLMOperationError("AI unavailable")
    safe = [{"name": sanitize_topic(s["name"]),
             "difficulty": int(s.get("difficulty") or 1)} for s in skills]
    data = _complete_json(
        prompts.role_quiz_prompt(
            sanitize_topic(role_title), safe,
            proficiency_level=proficiency_level,
            topics=[sanitize_topic(t) for t in topics] if topics else None,
            locale=locale),
        max_tokens=max(850, len(safe) * 330),
        salvage=_salvage_questions)
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


def analyze_diagnostic(per_skill: list[dict],
                       proficiency_level: int = None,
                       topics: list = None, locale: str = "en") -> dict | None:
    """Narrative report for pre-path results; None ⇒ deterministic fallback. Deps: _engine_available, prompts.diagnostic_analysis_prompt, _complete_json, _salvage_diagnostic, logger. Impl: normalizes gap_to_mastery→gap (pipeline-owned), caps narrative fields, converts any failure into None so callers render numbers-only. New optional params focus recommendations on topics, target the learner level, and select output locale."""
    if not _engine_available():
        logger.info("analyze_diagnostic skipped: AI unavailable")
        return None
    try:
        rows = [{**r, "gap": r.get("gap", r.get("gap_to_mastery", 0))}
                for r in per_skill]
        data = _complete_json(
            prompts.diagnostic_analysis_prompt(
                rows, proficiency_level=proficiency_level,
                topics=[sanitize_topic(t) for t in topics] if topics else None,
                locale=locale),
            max_tokens=750,
            salvage=_salvage_diagnostic)
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
    """Per-question explanations + advice; None ⇒ static recap fallback. Deps: _engine_available, prompts.explain_result_prompt, _complete_json, _salvage_explanations, logger. Impl: keeps only explanations whose question_index matches a graded row, converts any failure into None."""
    if not _engine_available():
        logger.info("explain_result skipped: AI unavailable")
        return None
    try:
        data = _complete_json(
            prompts.explain_result_prompt(responses), max_tokens=950,
            salvage=_salvage_explanations)
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
    """Bounded-autonomy level verdict; never moves beyond ±1/high-conf. Deps: _engine_available, prompts.review_level_prompt, _complete_json, logger. Impl: coerces output to safe ranges, applies delta only when confidence high & target 0..5; reported delta keeps suggestion even if clamping blocked application."""
    if not _engine_available():
        return {"delta": 0, "confidence": "low",
                "rationale": "AI unavailable", "applied": False,
                "final_level": max(0, min(5, current_level))}
    try:
        data = _complete_json(
            prompts.review_level_prompt(correct, total, difficulty,
                                        attempt_no, current_level),
            max_tokens=240, temperature=0.1)
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
