# SS-EDS: Gamification — DEPRECATED

> **⚠️ Feature removed.** XP, achievements, and levels deleted. Only `streaks` table retained.

> **Source**: Migrated from docs/SERVICES.md (gamification section)

## Purpose
Document the gamification system for SkillSynth, covering XP economy, levels, streaks, achievements, and their integration with the learning engine.

## Responsibilities
- Award XP on step completion (+10) and deduct on undo (-10)
- Calculate levels (each level = level * 100 XP)
- Manage daily streaks with milestones at 3/7/14/21/30/60/100 days
- Award achievements for milestones (1/10/50/100 steps completed)
- Provide aggregated gamification data for profile display

## Inputs
- Step completion events
- XP deduction events
- Daily login tracking

## Outputs
- Updated XP, level, streak fields on profile
- Achievement records
- Gamification API responses

## Dependencies
- 07-backend (gamification.py)
- 10-database (profiles: total_xp, level, streak fields)
- 11-learning-engine (step completion triggers)
- 12-realtime (SSE events for gamification updates)

## Sequence: Step Completion Gamification Flow
```
POST /api/steps/{step_id}/complete
  → Award +10 XP (db.execute UPDATE profiles SET total_xp = total_xp + 10)
  → Recalculate level (level = floor(0.5 * sqrt(1 + 8 * xp / 100)))
  → Update streak (check last_activity_date)
  → Check achievements (completion count milestones)
  → Fire SSE event: step_completed with xp_awarded
  → Return updated gamification data
```

## Gamification Functions
| Function | Effect |
|----------|--------|
| award_xp(db, profile_id, amount, reason) | +XP, level calc, awards level_N achievement |
| deduct_xp(db, profile_id, amount, reason) | -XP (floor 0), recalculates level down |
| update_streak(db, profile_id) | Daily streak: extends, resets on gap |
| check_and_award_completion_achievements(db, profile_id) | Milestones: 1/10/50/100 steps |
| get_user_gamification_data(db, profile_id) | Aggregated snapshot |

## State Diagram: Streak Lifecycle
```
[Active (daily)] → [Gap (>1 day)] → [Broken] → [Reset to 0] → [New Streak Begins]
      ↓
[Milestone reached (3/7/14/21/30/60/100)] → Achievement awarded
```

## ERD References
- profiles: total_xp, level, streak_count, last_activity_date, achievements (JSON), current_streak, longest_streak

## Rules
1. XP: +10 per step complete, -10 per undo
2. Level: each level requires `level * 100` XP total
3. XP floor: 0 (cannot go negative)
4. Streak: resets if gap > 1 day between activities
5. Achievements: level_N (every level), milestone_N (1/10/50/100 steps)
6. Gamification fires as side-effect of step completion (not standalone)

## Examples
- User with 450 XP → level = floor(sqrt(2*450+0.25)-0.5) = floor(29.97) = level 2
- User completes step daily for 7 days → streak_count=7, achievement "7_day_streak"
- User undoes step → -10 XP, if level drops → recalculate

## Edge Cases
- XP awarded but level calculation produces floating point → floor
- Streak broken due to timezone difference → use UTC date
- Concurrent step completions → serialized by DB transaction

## Failure Cases
- XP deduction goes below 0 → clamped to 0
- Achievement already awarded → idempotent (no duplicate)
- Streak count overflow → unlikely (max streak tracked in days)

## Recovery Procedures
1. Check gamification.py for XP calculation logic
2. Verify profile XP/level/streak fields in DB
3. Manually adjust via admin API if needed

## Refactoring Strategy
- Extract gamification into standalone service
- Add XP history table for audit trail
- Implement achievement categories (beyond just milestones)
- Add leaderboard functionality for social gamification
