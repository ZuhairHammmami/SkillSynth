"""LLM pipeline — validated ops over llm_engine (SS-AI). Sole consumer of llm_engine.complete and llm_prompts templates; called by routers/ai.py and the assess review hook. Each op gates on _engine_available() and degrades gracefully; parsing/salvage helpers live in llm_validation and are re-exported here for backward compatibility. Grounding context (from knowledge_layer) is threaded into prompts so the model answers from project data."""

import json
import logging
from typing import Callable

from backend.config import app_settings as settings
from backend.services import llm_prompts as prompts
from backend.services import settings_service
from backend.services import llm_validation as validation

logger = logging.getLogger(__name__)

_CONFIDENCES = ("high", "medium", "low")

# Re-exported parsing/salvage helpers so existing callers/tests keep working.
_extract_json = validation._extract_json
_iter_objects = validation._iter_objects
_valid_question = validation._valid_question
_salvage_questions = validation._salvage_questions
_salvage_diagnostic = validation._salvage_diagnostic
_salvage_explanations = validation._salvage_explanations
_salvage_topics = validation._salvage_topics
sanitize_topic = validation.sanitize_topic


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


def _complete_json(contract: dict, *, max_tokens: int,
                   temperature: float | None = None,
                   salvage: Callable[[str], dict | None] | None = None,
                   grammar: str | None = None) -> dict:
    """Complete a prompts contract with ONE corrective retry. Deps: _engine_factory().complete, _extract_json, optional salvage hook. Impl: reads contract system/user, appends prior parse error to a retry turn, forwards a temperature override and an optional constrained grammar; on failure offers raw payload to salvage, else raises LLMOperationError."""
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
                max_tokens=max_tokens, temperature=temperature,
                grammar=grammar if _grammar_wanted() else None)
            return validation._extract_json(raw)
        except (ValueError, json.JSONDecodeError) as exc:
            last_err = str(exc)[:120]
    if salvage is not None and raw is not None:
        salvaged = salvage(raw)
        if salvaged is not None:
            return salvaged
    raise LLMOperationError(f"invalid JSON after retry: {last_err}")


def _grammar_wanted() -> bool:
    """Whether constrained grammar output is enabled. Deps: settings.AI_GRAMMAR (default false). Impl: a runtime switch so grammar (validated on this build) can be opted in without touching call sites; off by default keeps behavior unchanged."""
    return bool(getattr(settings, "AI_GRAMMAR", False))


def _seeded_topics(skill_name: str, level: int) -> list[str]:
    """Deterministic fallback topic list for a skill at a level. Deps: builtins. Impl: produces min(3, level+1) reproducible strings so tests need no LLM."""
    return [f"Topic {i} for {skill_name} (level {level})"
            for i in range(1, min(3, level + 1) + 1)]


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


def generate_skill_quiz(skill_name: str, difficulty: int, n: int = 5,
                         exclude_texts=frozenset(),
                         proficiency_level: int = None,
                         topics: list = None, locale: str = "en",
                         context: str | None = None) -> list[dict]:
    """Validated single-skill MCQs for practice tests. Deps: _engine_available, sanitize_topic, prompts.skill_quiz_prompt, _complete_json, _valid_question. Impl: gates on engine (raise "AI unavailable"), validates output, raises LLMOperationError when nothing survives so callers fall back to seeded quizzes. New optional params target the learner level, focus on topics, select output locale, and inject a grounded context block (from knowledge_layer) so answers match the real skill."""
    if not _engine_available():
        raise LLMOperationError("AI unavailable")
    topic = sanitize_topic(skill_name)
    exclude = set(exclude_texts)
    data = _complete_json(
        prompts.skill_quiz_prompt(
            topic, difficulty, n, sorted(exclude),
            proficiency_level=proficiency_level,
            topics=[sanitize_topic(t) for t in topics] if topics else None,
            locale=locale, context=context),
        max_tokens=min(700, max(180, n * 95)),
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
                        topics: list = None, locale: str = "en",
                        context: str | None = None,
                        on_skill: Callable[[str, list[dict]], None] | None = None
                        ) -> list[dict]:
    """Validated role diagnostic quiz; items carry exact skill tag (batched).

    Deps: _engine_available, sanitize_topic, llm_batching.run_batch, _valid_
    question, logger. Impl: groups skills into batches, running ONE completion
    per batch instead of one per skill (a role has 12-20 skills → ~4x fewer
    completions on slow GPUs) via llm_batching, which splits and retries empty
    batches so coverage is never lost. Fires optional on_skill(name, chunk) per
    skill to stream progress. Raises LLMOperationError only when zero questions
    survive overall."""
    if not _engine_available():
        raise LLMOperationError("AI unavailable")
    from backend.services import llm_batching
    exclude = set(exclude_texts)
    batch_size = llm_batching.batch_size()
    named = [(sanitize_topic(s.get("name", "")), s)
             for s in skills if sanitize_topic(s.get("name", ""))]
    out: list[dict] = []
    seen: set[str] = set()
    for i in range(0, len(named), batch_size):
        batch = [s for _, s in named[i:i + batch_size]]
        by_skill = llm_batching.run_batch(batch, exclude, proficiency_level,
                                          topics, locale, context)
        for name, qs in by_skill.items():
            chunk: list[dict] = []
            for base in qs:
                if _valid_question(base, seen, exclude):
                    item = {**base, "skill": name,
                            "text": base["text"].strip()}
                    out.append(item)
                    seen.add(item["text"])
                    chunk.append(item)
            if chunk and on_skill is not None:
                on_skill(name, chunk)
    if not out:
        raise LLMOperationError("no valid role-quiz questions")
    return out


def analyze_diagnostic(per_skill: list[dict],
                       proficiency_level: int = None,
                       topics: list = None, locale: str = "en",
                       context: str | None = None) -> dict | None:
    """Narrative report for pre-path results; None ⇒ deterministic fallback. Deps: _engine_available, prompts.diagnostic_analysis_prompt, _complete_json, _salvage_diagnostic, logger. Impl: normalizes gap_to_mastery→gap (pipeline-owned), caps narrative fields, converts any failure into None so callers render numbers-only. New optional params focus recommendations on topics, target the learner level, select output locale, and inject grounded context."""
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
                locale=locale, context=context),
            max_tokens=400,
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
            prompts.explain_result_prompt(responses), max_tokens=500,
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
