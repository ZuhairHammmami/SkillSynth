# SS-EDS: Anti-Patterns

## Purpose
Document known anti-patterns, code smells, and practices to avoid in SkillSynth development. Provides concrete examples of what NOT to do and why.

## Responsibilities
- Identify and document anti-patterns discovered during development
- Provide alternatives and correct approaches
- Educate developers on common pitfalls
- Track anti-pattern frequency for refactoring prioritization

## Inputs
- Code review findings
- Bug root cause analysis
- Performance investigation results
- Developer experience reports

## Outputs
- Anti-pattern catalog
- Alternative solutions
- Prevention strategies

## Dependencies
- 37-clean-code (correct practices)
- 38-refactoring (fix anti-patterns)
- 48-style-guide (style violations)

## Anti-Pattern Catalog

### AP-001: N+1 Queries
**Problem**: Fetching related data in a loop (e.g., for each profile, fetch categories).
**Example**: 
```python
# BAD
for profile in profiles:
    categories = db.query(Category).join(skill_categories).filter(...).all()
```
**Impact**: 10 instances fixed in Phase 9, massive performance improvement.
**Fix**: Batch-fetch all related data in one query → convert to dict → O(1) lookup.

### AP-002: Hardcoded Arabic Strings
**Problem**: Arabic text hardcoded in components instead of using i18n.
**Impact**: Phase 5 fixed 33 files, zero tolerance going forward.
**Fix**: Always use `t('key')` from next-intl.

### AP-003: Gradients and Soft Shadows
**Problem**: Using CSS gradients, box-shadow with blur, or glassmorphism.
**Impact**: Banned by design principles (Phase 4).
**Fix**: Flat solid colors only. Hard drop shadow: `0 2px 0 0 rgba(0,0,0,0.5)`.

### AP-004: Physical CSS Properties in RTL
**Problem**: Using ml-/mr-, pl-/pr-, border-left/border-right in RTL context.
**Example**: `margin-left: 8px` instead of `margin-inline-start: 8px`.
**Fix**: Use logical properties: ms-/me-, ps-/pe-, border-s-/border-e-.

### AP-005: Services that Throw
**Problem**: Services throwing exceptions instead of returning fallback values.
**Fix**: All services must return fallback/empty result. Log error, never crash.

### AP-006: JSON Bridge Columns for M:N
**Problem**: Storing related IDs as JSON arrays on parent instead of junction tables.
**Example**: `skill_ids` JSON field on job_roles instead of job_role_skills table.
**Fix**: Phase 11 migrated to junction tables (skill_categories, skill_prerequisites, job_role_skills, path_skills).

### AP-007: transition: all
**Problem**: Using `transition: all` instead of specifying explicit properties.
**Impact**: Unintended animations, performance impact.
**Fix**: Always specify explicit properties: `transition: opacity 300ms ease-out`.

## ERD References
- Anti-patterns relate to database schema design (AP-006)
- Code-level anti-patterns linked to specific modules

## Rules
1. Anti-patterns must have concrete examples (BAD vs GOOD)
2. Each anti-pattern must document impact and fix
3. Anti-pattern catalog is reviewed quarterly
4. New anti-patterns added as discovered
5. Fixed anti-patterns marked with fix version

## Examples
- Good: `transition: transform 300ms ease-out, opacity 200ms ease`
- Bad: `transition: all 300ms`
- Good: junction tables for M:N relationships
- Bad: JSON array columns for M:N

## Edge Cases
- Legacy code containing anti-patterns → refactor when touched
- Third-party code with anti-patterns → document as known issue
- Performance optimization requiring anti-pattern → document trade-off

## Failure Cases
- Anti-pattern introduced → caught in code review
- Anti-pattern not documented → repeat offender
- Anti-pattern accepted without trade-off documentation → technical debt

## Recovery Procedures
1. Identify anti-pattern instance
2. Apply fix per documented solution
3. Add regression prevention (lint rule, test)

## Refactoring Strategy
- Use ESLint rules to catch anti-patterns automatically
- Add architectural tests to detect violations
- Schedule dedicated anti-pattern cleanup phases
- Track anti-pattern frequency in code quality metrics
