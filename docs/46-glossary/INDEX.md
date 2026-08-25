# SS-EDS: Glossary

## Purpose
Define the terms used in current SkillSynth code and documentation. Removed-feature vocabulary (gamification terms, synth-metaphor UI names, superseded schema names) is intentionally absent — if a term is not here, do not use it.

## Responsibilities
- Single, unambiguous definition per term
- Map each domain term to its owning table/endpoint

## Inputs
- Schema (src/migrations/003_reduced_schema.sql)
- Router/service naming

## Outputs
- Alphabetical glossary below

## Dependencies
- 05-domain (domain rules behind these terms)
- 10-database (table definitions)

## Glossary

### A–C
- **Access token**: JWT granting API access for 24h; renewal is re-login. No refresh token exists.
- **ADR**: Architectural Decision Record in docs/41-decision-records/.
- **Assessment**: Question set per skill/job-role; submit scores answers into user_skills (0–5).
- **Census**: Docs shorthand for the per-table dependent counts blocking a restricted delete; returned in the 409 body under the `dependents` key.
- **Cycle guard**: Validation rejecting self/direct/ancestor cycles for category parents and skill prerequisites with a 400.

### D–J
- **DAG**: Prerequisite graph over skills (skill_prerequisites); resolved by topological sort during path generation.
- **Force delete**: `?force=true` query flag on restricted deletes; executes the ERD cascade contract.
- **Gap analysis**: GET /api/learning/gaps — compares user_skills levels against role expectations.
- **Integrity net**: Global handler mapping uncaught SQLAlchemy IntegrityError to 409 (main.py).

### K–P
- **Learning velocity**: Completions per week, derived from trailing 30-day completions.
- **Mastery threshold**: proficiency_level ≥ 3; such skills are omitted from new generated paths.
- **Path / Path step**: Generated learning plan (paths) and its ordered steps (path_steps).
- **Proficiency level**: user_skills.proficiency_level, integer 0–5 written by assessment scoring.

### Q–Z
- **Restricted delete**: DELETE on skills/categories/job-roles that returns 409 with dependent counts when dependents exist (ADR-014).
- **RTL-first**: Arabic-default layout direction (`<html lang="ar" dir="rtl">`), English secondary via i18n.
- **SSE**: Server-Sent Events; the only push transport (/api/realtime/events, admin channel). No second socket channel exists.
- **Skill profile**: The user's user_skills rows viewed as {skill_name: level}; no JSON column stores it.
- **Soft delete (path)**: paths.deleted_at timestamp excluding a path from listings without row removal.
- **Step completion**: step_progress row with completed_at set; composite PK makes double-complete idempotent.
- **user_skills**: Table holding per-user proficiency; composite PK (user_id, skill_id), FKs CASCADE.

## ERD References
Every glossary entry above maps to tables documented in docs/40-diagrams/ERD.md.

## Rules
1. Documentation uses these terms verbatim; synonyms create drift
2. New feature → add its terms here in the same PR
3. Terms tied to removed features are deleted from this file when the feature dies

## Examples
- "census" appears only in prose about restricted deletes — the wire key it describes is `dependents`

## Edge Cases
- Term spans layers (proficiency level: schema + service + analytics) → defined once here, referenced everywhere

## Failure Cases
- Undocumented term spotted in review → either rename or add an entry

## Recovery Procedures
1. Conflicting definitions → fix the outlier doc, keep this file authoritative

## Refactoring Strategy
- Keep alphabetical flat list; split by letter only past ~60 entries
