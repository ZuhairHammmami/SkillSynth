"""Pure JSON parsing/salvage helpers for the LLM pipeline (SS-AI).

Split out of llm_pipeline.py to honor the <=300-line file rule. Holds only
stateless functions (no inference, no engine import): strict first-object
parsing, balanced-object recovery, and per-op salvage for quiz/diagnostic/
topics/explanation output. Re-exported by llm_pipeline for backward
compatibility with existing callers and tests.
"""

import json
import re


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


def _salvage_topics(text: str) -> dict | None:
    """Recover a topics list from broken topic output. Deps: _iter_objects. Impl: returns the first balanced object carrying a non-empty "topics" list, else None."""
    for obj in _iter_objects(text):
        if isinstance(obj, dict) and isinstance(obj.get("topics"), list):
            return obj
    return None


def sanitize_topic(text: str, limit: int = 120) -> str:
    """Strip braces/backticks/control chars; clamp length. Deps: re.sub. Impl: removes {,},<,>,`,\\ and control chars, trims, clamps to `limit`; used on skill/role names before prompts (injection hardening)."""
    cleaned = re.sub(r"[{}<>`\\]|[\x00-\x1f]", "", str(text))
    return cleaned.strip()[:limit]
