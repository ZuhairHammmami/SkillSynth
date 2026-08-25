# SS-EDS: Anti-Patterns

## Purpose
Catalog practices that are banned or were repeatedly harmful in SkillSynth, each with a concrete BAD/GOOD pair and the enforcement mechanism that catches it.

## Responsibilities
- Keep the catalog short, current, and checkable
- Name the guard (lint rule, test, review gate) per anti-pattern

## Inputs
- Code review findings
- Test failures with architectural root causes

## Outputs
- This catalog; additions require evidence from this codebase

## Dependencies
- 37-clean-code (positive counterpart)
- 48-style-guide (formatting-level violations)

## Catalog

### AP-001: N+1 Queries
**Problem**: Fetching related rows inside a loop.
```python
# BAD — one query per path
for p in paths:
    steps = db.query(PathStep).filter(PathStep.path_id == p.id).all()
```
**Fix**: Batch-fetch by id list once, build a dict, look up in O(1) — as `_path_progress_list` does via `completions_by_step_ids` (analytics_service.py).

### AP-002: Hardcoded UI Strings
**Problem**: Literal Arabic/English text inside components.
**Fix**: All copy through i18n message keys (`t('key')`); parity between ar/en files is a release gate. Enforced in frontend review.

### AP-003: Gradients, Glassmorphism, Soft Shadows
**Problem**: Decorative CSS effects violating the flat visual system.
**Fix**: Flat solid colors only; elevation via 1px borders and hard offsets. Enforced in design review against 20-ui-system tokens.

### AP-004: Physical CSS Properties in RTL
**Problem**: `ml-/mr-/pl-/pr-/border-left/right` break under `dir="rtl"`.
**Fix**: Logical properties only: `ms-/me-/ps-/pe-/border-s/e`, `margin-inline-start`. The app is RTL-first, so physical props fail visually immediately.

### AP-005: Services That Throw for Expected Failures
**Problem**: Raising exceptions for predictable conditions, forcing routers into try/except noise.
**Fix**: Services return result tuples `(payload, error_message)`; routers map them to status codes. Only genuinely unexpected errors may propagate to main.py handlers.

### AP-006: JSON Columns Where Relations Belong
**Problem**: Storing M:N or repeated references as JSON arrays instead of junction tables.
**Example**: The two documented exceptions on path_steps (`resource_ids`, `assessment_ids`) exist only as frozen wire-format bridges.
**Fix**: Real relations get real junction tables — `skill_prerequisites` (skill→prerequisite DAG) and `job_role_skills` (role→skill mappings), both composite-PK FK tables in src/migrations/003_reduced_schema.sql. New M:N data MUST be a junction table; do not add a third JSON bridge without an ADR.

### AP-007: `transition: all`
**Problem**: Unspecified transition properties animate unintended layout values.
**Fix**: Explicit property lists: `transition: opacity 200ms ease, transform 150ms ease`.

### AP-008: Skipping Integrity Guards for "Trusted" Callers
**Problem**: Assuming admin-only endpoints can skip FK/cycle validation because "admins don't send garbage".
**Fix**: Every mutating service runs the same ensure_* guards (services/catalog_integrity.py); tests prove 400/409 semantics for admin calls too (tests/test_catalog_integrity.py). The IntegrityError net is a safety net, never the intended validation layer.

### AP-009: Reintroducing Removed Features
**Problem**: Rebuilding gamification counters, notification tables, role hierarchies, or second transports "temporarily".
**Fix**: Removals are ADR-recorded decisions (ADR-013). Resurrection requires a superseding ADR first — no code before the ADR.

### AP-010: Docs Drift
**Problem**: Documentation describing removed commands/files (legacy seed scripts, deleted layers) or invented endpoints.
**Fix**: Docs cite only existing files/commands; grep gates for stale terms run before docs commits (see 19-conventions).

## Rules
1. Every entry keeps its BAD/GOOD example current with real symbol names
2. An anti-pattern without an enforcement mechanism is a wish, not a rule — add the lint/test or cut the entry
3. Fixed systemic issues graduate here so they stay fixed

## Examples
- GOOD junction usage: learning graph endpoint reads skill_prerequisites edges directly (learning_service)
- BAD junction avoidance: appending prerequisite ids to a skills.prereq_ids JSON column

## Edge Cases
- Performance-critical denormalization → allowed only with a measured benchmark and an ADR note

## Failure Cases
- Reviewer spots a violation post-merge → fix forward plus add the missing guard

## Recovery Procedures
1. Sweep with targeted greps (e.g., `rg "transition:\s*all" src/frontend`), fix, add CI grep where cheap

## Refactoring Strategy
- Quarterly pass: delete entries guarding against things that can no longer occur
