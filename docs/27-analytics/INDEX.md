# SS-EDS: Analytics

## Purpose
Document the analytics system for SkillSynth, covering learner analytics dashboard, admin reports, skill growth tracking, learning velocity, and system health metrics.

## Responsibilities
- Provide learner analytics (XP, level, velocity, streak, skill growth, recent activity)
- Generate admin reports (user activity, content engagement, system health)
- Track skill proficiency growth over time
- Compute learning velocity (weekly/monthly)
- Serve aggregated dashboard data

## Inputs
- Step completion data
- Assessment results
- User profile data
- Event logs

## Outputs
- Analytics dashboard API responses
- Admin report data
- Skill growth trajectories
- Learning velocity metrics

## Dependencies
- 07-backend (analytics_router.py)
- 10-database (step_progress, assessment_results, activity_log)
- ~~28-gamification (XP, level)~~, streak data (streaks retained)

## Sequence: Analytics Dashboard Load
```
User → Navigate to /analytics → GET /api/analytics/dashboard
  → Aggregate path progress
  → Compute skill growth
  → Calculate learning velocity
  → Fetch recent activity
  → Return combined dashboard data
  → Render charts with dynamic imports
```

## State Diagram: Analytics Data Freshness
```
[Real-time] → Step completions, XP updates
[Cached (30s)] → Dashboard aggregates
[Daily] → Admin reports
[Weekly] → Learning velocity trends
[Monthly] → Skill growth trajectories
```

## Analytics Endpoints
| Endpoint | Purpose |
|----------|---------|
| GET /api/analytics/dashboard | All analytics aggregated |
| GET /api/analytics/path-progress/{path_id} | Per-path step-by-step progress |
| GET /api/analytics/skill-growth | Skill proficiency breakdown + gaps |
| GET /api/analytics/learning-history | Last 20 completions + 7-day daily activity |
| GET /api/analytics/learning-velocity | Weekly/monthly velocity |

## Admin Report Endpoints
| Endpoint | Purpose |
|----------|---------|
| GET /api/admin/analytics/overview | 7-day admin overview |
| GET /api/admin/reports/user-activity | User stats |
| GET /api/admin/reports/content-engagement | Content stats |
| GET /api/admin/reports/system-health | System status |
| GET /api/admin/reports/most-active-users | Top 10 users |
| GET /api/admin/reports/most-requested-skills | Top skills |

## ERD References
- step_progress: user_id, step_id, completed_at, score
- events: category, action, entity_type
- profiles: ~~total_xp, level,~~ streak_count, last_activity_date

## Rules
1. Dashboard aggregates must respond < 50ms (currently 21.4ms)
2. Charts dynamically imported to reduce bundle size
3. All analytics data is read-only from materialized queries
4. Admin reports paginate at 20 items per page
5. Skill growth calculated from assessment result history

## Examples
- Learning velocity: steps completed per week over last 30 days → trend line
- Skill growth: skill_proficiency JSON before/after assessment → delta chart

## Edge Cases
- User with no completions → empty state with "Start a path to see analytics"
- Single data point → no trend line, show current value only
- Very high XP/level → display formatting without overflow

## Failure Cases
- Analytics aggregates fail on empty database → return zeros
- Chart rendering fails → error boundary shows fallback message
- Report takes too long → timeout at 30s

## Recovery Procedures
1. Check step_progress and activity_log tables for data
2. Verify analytics_router endpoint works
3. Check admin report generation logic

## Refactoring Strategy
- Pre-materialize dashboard aggregates for faster queries
- Add export functionality (CSV, PDF) for reports
- Implement predictive analytics using historical trends
