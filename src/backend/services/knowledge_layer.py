"""Knowledge layer — persistent in-memory catalog digest for SS-AI grounding.

Built lazily on first AI use, refreshed on catalog writes, read-only. Provides
skill_context(skill_id) (one skill's grounded block) and knowledge_digest() (a
compact whole-catalog reference) that llm_prompts/pipeline inject into prompts
so the local model is accurate to the project's own skills/categories/bank.
Invalidated via catalog_service.invalidate_skill_cache() so writes trigger a
rebuild. Depends on catalog_repository, assess_repository and assess entities.
"""

import logging
import threading

from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository as repo

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_digest: dict | None = None

_BANK_PER_SKILL = 4
_DESC_TRUNC = 2000
_LINE_TRUNC = 140


def invalidate() -> None:
    """Drop the cached digest so the next access rebuilds it.

    Called by catalog_service.invalidate_skill_cache() on every catalog write
    (skill/category/job-role changes) so grounded prompts never go stale even
    though the engine cannot be retrained.
    """
    global _digest
    with _lock:
        _digest = None


def _ensure_built(db) -> dict:
    """Return the digest, building it once under a lock (double-checked).

    Depends on _build(); called by every public accessor so the catalog is
    read only when AI grounding is actually requested.
    """
    global _digest
    if _digest is not None:
        return _digest
    with _lock:
        if _digest is None:
            _digest = _build(db)
    return _digest


def _build(db) -> dict:
    """Read the whole catalog into a compact, queryable digest.

    Depends on repo.get_all_skills/get_categories_map/get_prereqs_by_skill_ids
    and arepo.get_assessments_for_skills + a batched question query. Uses few
    queries (no per-row N+1). Returns {skills, categories, prereq_names, bank}
    where skills is id -> grounded block and bank is skill_id -> sample prompts.
    """
    skills = repo.get_all_skills(db)
    cat_map = repo.get_categories_map(db)
    prereqs = repo.get_prereqs_by_skill_ids(db, [s.id for s in skills])
    assessments = arepo.get_assessments_for_skills(db, [s.id for s in skills])
    bank = _bank_samples(db, assessments)
    out = {"categories": _category_blocks(cat_map), "prereq_names": {},
           "skills": {}, "bank": bank}
    for s in skills:
        cat = cat_map.get(s.category_id)
        out["prereq_names"][s.id] = [p.name for p in prereqs.get(s.id, [])]
        out["skills"][s.id] = {
            "id": s.id, "name": s.name,
            "description": (s.description or "")[:_DESC_TRUNC],
            "topics": s.topics, "difficulty": s.difficulty_level or 1,
            "category": cat.name if cat else None,
            "category_description":
                (cat.description or "")[:600] if cat else None,
        }
    return out


def _category_blocks(cat_map: dict) -> dict[int, dict]:
    """Compact category blocks {id: {"name","description"}} for digest lines."""
    return {cid: {"name": c.name, "description":
                  (c.description or "")[:600]}
            for cid, c in cat_map.items()}


def _bank_samples(db, assessments: dict[int, object]) -> dict[int, list[str]]:
    """skill_id -> up to _BANK_PER_SKILL existing bank prompts.

    Depends on a batched AssessmentQuestion query keyed by the assessments
    map (skill_id -> Assessment). Called by _build once.
    """
    from backend.entities.assessment import AssessmentQuestion
    assessment_ids = [a.id for a in assessments.values()]
    if not assessment_ids:
        return {}
    rows = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.assessment_id.in_(assessment_ids))
        .order_by(AssessmentQuestion.assessment_id,
                  AssessmentQuestion.position)
        .all()
    )
    per_a: dict[int, list[str]] = {}
    for r in rows:
        per_a.setdefault(r.assessment_id, []).append(r.prompt)
    by_skill: dict[int, list[str]] = {}
    for skill_id, a in assessments.items():
        by_skill[skill_id] = per_a.get(a.id, [])[:_BANK_PER_SKILL]
    return by_skill


def skill_context(db, skill_id: int, n_bank: int = _BANK_PER_SKILL) -> str:
    """A bounded grounding block for one skill, or "" when unknown.

    Depends on _ensure_built; called by pipeline callers (ai router, step
    jobs) to enrich skill-quiz prompts. Renders the skill's description,
    topics, category and up to n_bank existing questions so the model answers
    from project truth. Returns "" (no grounding) for missing skills or a
    skill with neither description nor topics, keeping no-grounding fallback
    identical.
    """
    digest = _ensure_built(db)
    skill = digest["skills"].get(skill_id)
    if not skill or not (skill["description"] or skill["topics"]):
        return ""
    lines = []
    if skill["description"]:
        lines.append(f"- Description: {skill['description']}")
    if skill["topics"]:
        lines.append("- Topics: " + "; ".join(
            str(t) for t in skill["topics"][:15]))
    if skill["category"]:
        lines.append(f"- Category: {skill['category']}")
    prereqs = digest["prereq_names"].get(skill_id, [])
    if prereqs:
        lines.append("- Prerequisites: " + "; ".join(prereqs[:6]))
    samples = digest["bank"].get(skill_id, [])[: n_bank]
    if samples:
        lines.append("- Existing bank questions (match their style/level):")
        for s in samples:
            lines.append(f'  - "{s.strip()[:160]}"')
    return "Project reference for this skill:\n" + "\n".join(lines)


def knowledge_digest(db, limit: int = 150) -> str:
    """A compact whole-catalog reference (one line per skill).

    Depends on _ensure_built; called to ground role/diagnostic prompts that
    span many skills. Each line: "name | category | top-3 topics". Clamped to
    `limit` lines to protect the context budget on small VRAM.
    """
    digest = _ensure_built(db)
    lines = []
    for sid in sorted(digest["skills"]):
        s = digest["skills"][sid]
        topics = "; ".join(str(t) for t in (s["topics"] or [])[:3])
        line = f"{s['name']} | {s['category'] or ''} | {topics}".rstrip(" |")
        lines.append(line[:_LINE_TRUNC])
        if len(lines) >= limit:
            break
    if not lines:
        return ""
    return "Catalog of project skills (name | category | topics):\n" + \
        "\n".join(lines)
