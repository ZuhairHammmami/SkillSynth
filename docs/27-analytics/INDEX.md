# SS-EDS: Analytics

## Purpose
Document the learner analytics endpoints and their exact payload keys, implemented in src/backend/services/analytics_service.py. All aggregates derive from step_progress completions and user_skills proficiency; there are no XP, level, or streak metrics anywhere in the system.

## Responsibilities
- Serve the learner dashboard aggregate (GET /api/analytics/dashboard)
- Track per-skill proficiency buckets (mastered ≥ 3, learning 1–2, not_started 0)
- Compute learning velocity from 7/30-day completion counts
- Expose admin aggregated reports (GET /api/admin/reports/aggregated, /system-health)

## Inputs
- step_progress rows (completed_at NOT NULL counts as a completion)
- user_skills.proficiency_level (0–5, written by assessment scoring)
- paths/path_steps for per-path progress blocks

## Outputs
- Four Bearer-authenticated GET endpoints under /api/analytics/*
- Admin report payloads via admin_service.py

## Dependencies
- 07-backend (routers/analytics.py → analytics_service.py → repositories/learning_repository.py)
- 10-database (step_progress, user_skills, paths, path_steps)

## Dashboard Keys (learner_dashboard, wire-frozen)
| Key | Meaning |
|-----|---------|
| total_paths | Paths owned by the user (soft-deleted excluded) |
| total_completed_steps / completed_steps | Lifetime completions (legacy duplicate key kept) |
| total_steps | Steps across the user's paths |
| completion_rate | completed/total %, one decimal |
| mastered_skills / learning_skills | Profile skills with level ≥ 3 / 1–2 |
| total_skill_areas | Distinct skills in the user's profile |
| weekly_completions | Completions in trailing 7 days |
| total_hours · completed_hours · remaining_hours | Estimated hours and progress-scaled split |
| learning_velocity | 30-day completions averaged to per-week |
| recent_activity | Last 5 {type:"step_completed", description, date} items |
| path_progress | Per-path {path_id, path_title, total_steps, completed_steps, percentage} |

## Endpoint Payloads
| Endpoint | Keys |
|----------|------|
| GET /api/analytics/skill-growth | skills[{skill, level, status}], mastered_count, in_progress_count, not_started_count, weak_skills[3], strong_skills[3], knowledge_gaps |
| GET /api/analytics/path-progress/{id} | path_id, total_steps, completed_steps, completion_percentage, hour splits, estimated_weeks, goal_role, step_progress[] |
| GET /api/analytics/learning-history | recent_activity[{step_title, path_title, ids, completed_at}], total_completions, weekly_completions, daily_activity[7 days] |
| GET /api/analytics/learning-velocity | weekly_velocity, monthly_velocity, total_completions, total_hours, average_per_week |

Mastery rule shared by dashboard/growth: `_status_for` — level ≥ 3 mastered, > 0 learning, else not_started (analytics_service.py:17).

## Sequence: Dashboard Load
```
Frontend analytics page → GET /api/analytics/dashboard (Bearer JWT)
  → analytics_service.learner_dashboard
    → count_paths/count_completions/count_steps + sum_total_hours
    → get_skill_profile (user_skills) → bucket mastered/learning
    → _path_progress_list (batch step fetch, single completions query)
  → JSON payload rendered by charts + stat cards
```

## Rules
1. Key sets are frozen for wire compatibility (see module docstring, analytics_service.py:1)
2. All aggregates computed on request — no materialized views, no cache layer
3. Empty profile → zeros across counters; empty activity lists, never errors
4. Admin reports live in admin_service.py (most_active_users, count_paths) served through /api/admin/reports/aggregated
5. No gamification metrics exist: no XP, level, streak, or achievement fields

## Examples
- User completed 9 steps in 30 days → learning_velocity = round(9/(30/7), 1) = 2.1
- skill-growth weak_skills = first 3 learning-level skills sorted by level desc

## Edge Cases
- Path with zero steps → percentage 0 (guard at analytics_service.py:36)
- Not the path owner → path-progress returns None → router maps to 404

## Failure Cases
- DB unreachable → FastAPI 500 via global handler; frontend error boundary renders retry UI

## Recovery Procedures
1. `PYTHONPATH=src python -m pytest tests/test_analytics.py -q` (8 tests)
2. Inspect step_progress/user_skills via /api/admin/db-inspector

## Refactoring Strategy
- Keep key freezing discipline: new fields append-only, removals require a frontend release
- Consider ETag caching if dashboards become hot paths
