# SS-EDS: Domain

## Purpose
Define the core domain model and ubiquitous language for SkillSynth: skills, prerequisites, job roles, assessments, proficiency, learning paths, and progress. Bounded contexts are Catalog, Assessment, Learning, and Engagement.

## Responsibilities
- Document the ubiquitous language of the learning domain
- Define bounded contexts and their aggregates
- Map user actions to domain outcomes

## Inputs
- Learning-science constraints (prerequisite ordering)
- Assessment scoring rules
- Catalog structure (categories, job roles)

## Outputs
- Domain glossary (docs/46-glossary/)
- Context map (this document)
- Invariants enforced by services

## Dependencies
- 10-database (domain persistence — 15 tables)
- 11-learning-engine (core domain logic)

## Sequence: Path Generation Domain Flow
```
Learner → Wizard (job role + preferences) → Skill Scoring → Prerequisite Topo Sort
        → Path + Steps → Step Completion → Progress Dashboard
```

## State Diagram: Learning Path Lifecycle
```
[Generated] → [In Progress] → [Completed]
                  ↓
           [Step Undone] → [In Progress]
```

## ERD References
- users — identity and is_admin flag
- categories / skills / skill_prerequisites / job_roles / job_role_skills / resources — catalog context
- assessments / assessment_questions / assessment_results / user_skills — assessment context
- paths / path_steps / step_progress — learning context
- activity_log — engagement/audit context

## Bounded Contexts
| Context | Aggregates | Notes |
|---------|-----------|-------|
| Catalog | Category tree, Skill (+prerequisites), JobRole (+skill weights), Resource | Admin-managed; delete-gated by dependency census |
| Assessment | Assessment, Question, Result | Questions normalized in assessment_questions; options JSON |
| Learning | Path, PathStep, StepProgress, UserSkill | Deterministic generation; no LLM in the loop |
| Engagement | ActivityLog entry | Append-only audit trail |

## Domain Rules
1. Skill proficiency is an integer 0–5 stored per user in user_skills.proficiency_level; scoring computes `round(correct / total × 5)` clamped to [0,5], and unanswered skills keep their prior level
2. Prerequisites form a DAG over skill_prerequisites; generation orders skills with Kahn's algorithm so prerequisites precede dependents
3. Job roles weight skill relevance via job_role_skills; wizard scoring ranks skills for inclusion
4. Paths belong to one user; steps reference resources and/or assessments by id
5. Completing a step writes step_progress.completed_at; undo removes it

## Examples
- Learner scoring 4/5 on a skill's questions → proficiency_level 4 for that skill
- A path never schedules a skill before its prerequisites (topological invariant, tested in tests/test_learning.py)

## Edge Cases
- Empty skill profile (new user) → all candidate skills eligible
- Cycle inserted into skill_prerequisites via API → rejected 400 before it can reach the generator
- Unanswered skills during submission retain their previous level (no silent downgrade)

## Failure Cases
- Assessment scoring with zero questions → guarded upstream (question sets are non-empty)
- Generation with no eligible skills → empty/error response surfaced to wizard UI

## Recovery Procedures
1. Log domain errors to activity_log with full context
2. Correct catalog data via admin CRUD; regenerate the path

## Refactoring Strategy
- Domain logic stays inside services/ modules (learning_service.py, assess_service.py, wizard_service.py, catalog_integrity.py)
- New domain concepts require an ADR before schema or service changes

Historical note (one line): gamification bounded contexts were removed outright; see docs/41-decision-records/.
