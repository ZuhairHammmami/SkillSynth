"""tests/test_knowledge_layer.py — SS-AI catalog grounding digest.

Exercises knowledge_layer (new service) against the seeded test DB: the lazy
digest builds full skill coverage, skill_context returns a grounded block for
real skills but "" for unknown ones, the whole-catalog digest is bounded, and
invalidate() forces a rebuild. No LLM inference is involved.
"""

from backend.services import knowledge_layer


def test_digest_builds_all_skills(db_session):
    """The digest contains every seeded skill with grounding fields."""
    knowledge_layer.invalidate()
    digest = knowledge_layer._ensure_built(db_session)
    assert digest["skills"]
    for skill in digest["skills"].values():
        assert skill["name"]
        # at least one grounding field (description or topics) present
        assert skill["description"] or skill["topics"]


def test_skill_context_grounded_for_known_skill(db_session):
    """A known skill yields a Project-reference block mentioning it."""
    knowledge_layer.invalidate()
    first_id = sorted(
        knowledge_layer._ensure_built(db_session)["skills"])[0]
    ctx = knowledge_layer.skill_context(db_session, first_id)
    assert ctx.startswith("Project reference for this skill:")


def test_skill_context_empty_for_unknown(db_session):
    """Unknown skill_id → "" so callers keep the no-grounding fallback."""
    knowledge_layer.invalidate()
    assert knowledge_layer.skill_context(db_session, 99999999) == ""


def test_knowledge_digest_bounded_lines(db_session):
    """The catalog digest is clamped to the requested line limit."""
    knowledge_layer.invalidate()
    d = knowledge_layer.knowledge_digest(db_session, limit=2)
    assert d.startswith("Catalog of project skills")
    assert d.count("\n") <= 2


def test_invalidate_forces_rebuild(db_session):
    """invalidate() drops the cached dict so the next access rebuilds it."""
    knowledge_layer.invalidate()
    first = knowledge_layer._ensure_built(db_session)
    knowledge_layer.invalidate()
    second = knowledge_layer._ensure_built(db_session)
    assert first is not second
