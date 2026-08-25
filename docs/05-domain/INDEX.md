# SS-EDS: Domain

## Purpose
Define the core domain model, ubiquitous language, and bounded contexts for SkillSynth. Establishes shared understanding of learning paths, assessments, and analytics.

## Responsibilities
- Document ubiquitous language for the learning domain
- Define bounded contexts (Learning Engine, Assessment, Streaks~~, Gamification~~ — XP/level/achievements removed)
- Map domain events to system events
- Maintain glossary (docs/46-glossary/)

## Inputs
- Learning science research
- Prerequisite DAG concepts
- Gamification patterns (XP, streaks, achievements, levels) — **DEPRECATED: XP/achievements removed, streaks retained**

## Outputs
- Domain glossary
- Context map
- Event storming results

## Dependencies
- 10-database (domain persistence)
- 11-learning-engine (core domain logic)
- 46-glossary (vocabulary)

## Sequence: Learning Path Generation Domain Flow
```
Learner → Assessment → Skill Profile → Path Generator → Path → Steps → Resources → Completion → ~~Gamification Events~~ (streak update only)
```

## State Diagram: Learning Path Lifecycle
```
[Draft] → [Active] → [In Progress] → [Completed] → [Archived]
                ↓                        ↓
         [Regenerated]           [Archived with Results]
```

## ERD References
- profiles: skill_profile JSON, ~~total_xp, level,~~ streak fields (streaks retained)
- paths: skill_ids JSON, status
- path_steps: step_number, resource_ids, assessment_ids
- step_progress: composite PK (user_id, step_id); completed_at marks completion

## Domain Rules
1. Skill proficiency: 0=not_started, 1-2=learning, 3-4=competent, 5=mastered
2. Mastered skills (≥3) are skipped in path generation
3. ~~XP: +10 per step complete, -10 per undo~~ (removed)
4. ~~Level: each level = level * 100 XP~~ (removed)
5. Prerequisites form a DAG, sorted via Kahn's algorithm

## Examples
- Learner with skill_profile {"html": 4, "css": 3, "javascript": 2} generates a path skipping HTML/CSS
- Completing step updates streak (~~awards 10 XP, checks achievements at 1/10/50/100 steps~~ XP/achievements removed)

## Edge Cases
- Skill profile empty (new user) — no skills skipped
- Prerequisite cycle in data — Kahn's algorithm detects and skips cyclic edges
- ~~XP floor at 0 — undo cannot reduce below zero~~ (removed)

## Failure Cases
- Assessment scoring produces NaN → default to 0
- Path generation with no skills available → empty path with error message

## Recovery Procedures
1. Log domain errors with full context
2. Fall back to static JSON rules if DB data is inconsistent
3. Admin override for skill profile adjustments

## Refactoring Strategy
- Domain logic lives in dedicated modules (generator.py, assessor.py, ~~gamification.py~~)
- Bounded contexts communicate through domain events
- Regularly review ubiquitous language with stakeholders
