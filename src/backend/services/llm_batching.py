"""Batched role-quiz assembly for the LLM pipeline (SS-AI).

Split out of llm_pipeline.py to honor the <=300-line file rule. Owns the
grouping/fallback logic that lets a role quiz (12-20 skills) run as a few
batched completions instead of one per skill. Imports pipeline helpers
lazily inside functions so loading this module never starts inference and
avoids a module-load cycle with llm_pipeline.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover — typing only, never imported at runtime
    from backend.services import llm_pipeline as _pipe

_ROLE_BATCH = 4
"""Max skills generated per single batched completion (2 Q each)."""


def batch_size() -> int:
    """Return the configured skills-per-completion batch size. Deps: module
    constant _ROLE_BATCH. Impl: a tiny accessor so generate_role_quiz reads
    the same value used by tests without importing this module's internals."""
    return _ROLE_BATCH


def run_batch(batch: list[dict], exclude: set, proficiency_level,
              topics, locale, context) -> dict[str, list[dict]]:
    """One batched completion for a skill group; split-and-retry when empty.

    Deps (lazy): llm_pipeline._complete_json/_salvage_questions/sanitize_topic/
    role_quiz_batch_prompt, llm_pipeline.generate_skill_quiz, logger. Impl: one
    call asks all questions; keeps only items whose sanitized tag matches a
    batch member, grouped by that skill (batch order preserved). An all-empty
    batch splits in half and recurses; a single-skill half that still fails
    falls back to _run_one_skill. Never raises — an all-empty batch returns {}
    for the caller to skip."""
    if not batch:
        return {}
    from backend.services import llm_pipeline as pipe
    from backend.services import llm_prompts as prompts
    names = [pipe.sanitize_topic(s.get("name", "")) for s in batch]
    data = pipe._complete_json(
        prompts.role_quiz_batch_prompt(
            batch, proficiency_level=proficiency_level, topics=topics,
            locale=locale, context=context),
        max_tokens=min(700, len(batch) * 190),
        salvage=pipe._salvage_questions)
    grouped: dict[str, list[dict]] = {n: [] for n in names}
    for q in data.get("questions", []):
        tag = pipe.sanitize_topic(q.get("skill", ""))
        if tag not in grouped:
            continue
        base = {k: q[k] for k in ("text", "options", "correct_index")}
        if pipe._valid_question(base,
                                {x["text"] for x in grouped[tag]}, exclude):
            grouped[tag].append(base)
    if any(grouped.values()):
        return grouped
    if len(batch) == 1:
        return _run_one_skill(batch[0], exclude, proficiency_level,
                              topics, locale, context)
    half = len(batch) // 2
    merged: dict[str, list[dict]] = {}
    for sub in (batch[:half], batch[half:]):
        for k, v in run_batch(sub, exclude, proficiency_level,
                              topics, locale, context).items():
            merged.setdefault(k, []).extend(v)
    return merged


def _run_one_skill(skill: dict, exclude: set, proficiency_level,
                   topics, locale, context) -> dict[str, list[dict]]:
    """Per-skill fallback returning {name: questions} or {} on failure.

    Deps (lazy): llm_pipeline.generate_skill_quiz/sanitize_topic, logger. Impl:
    delegates to the single-skill generator (n=2), swallowing LLMOperationError
    so one bad skill never aborts the quiz; the terminal step of run_batch."""
    import logging
    from backend.services import llm_pipeline as pipe
    logger = logging.getLogger(__name__)
    name = pipe.sanitize_topic(skill.get("name", ""))
    s_topics = ([pipe.sanitize_topic(t) for t in (skill.get("topics") or [])]
                or None)
    try:
        qs = pipe.generate_skill_quiz(
            name, int(skill.get("difficulty") or 1), n=2,
            exclude_texts=exclude, proficiency_level=proficiency_level,
            topics=s_topics or topics, locale=locale, context=context)
        return {name: qs}
    except pipe.LLMOperationError as exc:
        logger.warning("role quiz: skipped skill %r: %s", name, exc)
        return {}
