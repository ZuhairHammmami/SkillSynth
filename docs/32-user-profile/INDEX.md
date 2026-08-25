# SS-EDS: User Profile

## Purpose
Document the user profile system for SkillSynth, covering profile data model, skill profile management, preferences, and learner-facing profile features.

## Responsibilities
- Manage user profile data (email, name, avatar, preferences)
- Maintain skill proficiency profile (skill_profile JSON)
- Handle gamification profile (~~achievements, XP, level~~ — **removed, streaks retained**)
- Provide profile editing and viewing functionality

## Inputs
- Registration data (email, password, full_name)
- Assessment results (skill_profile updates)
- Gamification events (XP, level, streak updates)
- User preferences (language, learning format)

## Outputs
- Profile API responses
- Updated skill_profile JSON
- ~~Updated gamification fields~~ (removed)

## Dependencies
- 10-database (profiles table)
- 07-backend (auth_router.py, user profile endpoints)
- ~~28-gamification (XP, level, achievements)~~ streaks only retained
- 11-learning-engine (skill profile used for path generation)

## Sequence: Profile Update Flow
```
User → Edit Profile → PUT /api/auth/users/me
  → Validate fields
  → Update profile record
  → Return updated profile
  → Invalidate React Query (user.me)
```

## Profile Data Model
| Field | Type | Source |
|-------|------|--------|
| email | string (unique) | Registration |
| full_name | string | Registration |
| hashed_password | string (bcrypt) | Registration |
| is_admin | boolean | Admin assignment |
| ~~role_id~~ | ~~int (FK→roles)~~ | ~~Role assignment~~ **REMOVED** |
| skill_profile | JSON | Assessment results |
| streak_count | int | Gamification (retained) |
| current_streak | int | Gamification (retained) |
| longest_streak | int | Gamification (retained) |
| last_activity_date | date | Gamification (retained) |
| preferences | JSON | User settings |
| ~~total_xp, level, achievements~~ | | **REMOVED** |
| avatar_url | string (nullable) | Upload |

## Skill Profile JSON
```json
{
  "html": 4,
  "css": 3,
  "javascript": 2,
  "python": 0
}
```
Levels: 0=not_started, 1-2=learning, 3-4=competent, 5=mastered

## ERD References
- profiles: all above fields ~~role_id FK→roles~~ (removed from profiles)
- assessment_results: skill profile source data

## Rules
1. Email must be unique
2. Password: min 8 chars, ≥1 uppercase, ≥1 digit
3. Skill levels: 0-5 integer only
4. XP and level are calculated, not manually editable
5. Profile changes propagate to path generation on next assessment

## Examples
- New user: skill_profile = {}~~, total_xp = 0, level = 1~~
- ~~After 10 step completions: total_xp = 100, level = 1 (still, since level 2 = 200 XP)~~ (XP/level removed)

## Edge Cases
- Email change requires re-verification (future)
- Profile deletion cascades to paths, completions, assessment results
- Empty skill_profile → all skills considered "not started"

## Failure Cases
- Duplicate email on registration → 409 Conflict
- Invalid skill level (e.g., 6) → validation error
- Profile not found → 404

## Recovery Procedures
1. Check profiles table for user record
2. Verify auth token matches profile_id
3. Use admin API to update profile if needed

## Refactoring Strategy
- Add profile versioning for skill profile history
- Implement email verification flow
- Add profile export (JSON download) feature
- Separate user settings into preferences table
