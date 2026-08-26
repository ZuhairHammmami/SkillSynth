# SS-EDS: User Profile

## Purpose
Document the user identity model and how skill proficiency is represented. The users table carries identity only (id, email, hashed_password, full_name, is_admin, timestamps); the skill profile is not a JSON column — it is the set of user_skills rows.

## Responsibilities
- Own account identity: registration, login, profile read/update (src/backend/routers/auth.py)
- Expose ProfileUpdate with a single editable field: full_name (src/backend/dto/auth.py)
- Derive the skill profile from user_skills.proficiency_level (0–5) written by assessment scoring

## Inputs
- Registration payload {email, password, full_name?} (RegisterInput)
- PUT /api/auth/me body {full_name?} (ProfileUpdate — nothing else is updatable)
- Assessment submissions upserting user_skills via assess_repository

## Outputs
- ProfileOut {email, full_name} from GET/PUT /api/auth/me
- Skill profile consumed by path generation and analytics (27-analytics)

## Dependencies
- 10-database (users, user_skills; DDL src/migrations/003_reduced_schema.sql)
- 14-security (JWT 24h access token, lockout after 5 failed logins → 15 min)
- 11-learning-engine (user_skills feeds prerequisite filtering)

## Data Model
| Table.Field | Type | Notes |
|-------------|------|-------|
| users.email | string unique | login identifier |
| users.hashed_password | string | bcrypt |
| users.full_name | string nullable | the only user-editable profile field |
| users.is_admin | bool | binary admin gate (33-admin-profile) |
| users.created_at / updated_at | timestamp | server defaults |
| user_skills.user_id + skill_id | composite PK | FKs CASCADE to users/skills |
| user_skills.proficiency_level | int 0–5 | default 1; last_assessed_at nullable |

Removed with ADR-013: profiles table merge, streak columns, XP/level fields, role_id, preferences JSON, avatar_url. No gamification columns exist anywhere.

## Sequence: Profile Update Flow
```
User edits name → PUT /api/auth/me {full_name} (Bearer JWT)
  → auth_service validates + sanitizes full_name
  → identity repository updates users row
  → ProfileOut returned → frontend invalidates the me query
```

## Skill Profile Access Pattern
```python
# repositories/assess_repository.get_skill_profile(db, user_id)
# → {skill_name: proficiency_level} dict built from user_skills ⨝ skills
{"html": 4, "css": 3, "javascript": 2}
```
Buckets used across the app: level ≥ 3 mastered · 1–2 learning · 0/absent not_started.

## Rules
1. Email is immutable through the API (no email-change endpoint exists)
2. Password changes go through POST /api/auth/change-password (current password required)
3. proficiency_level is clamped to 0–5 by scoring logic before upsert
4. Deleting a user cascades to user_skills, paths, path_steps, step_progress
5. The wizard treats absent user_skills rows as level 0 (skill still enters the plan)

## Examples
- New user: zero user_skills rows → dashboard shows total_skill_areas = 0
- After assessment: one row per assessed skill with clamped level and last_assessed_at

## Edge Cases
- full_name null or empty string → sanitized on write (dto/auth.py validator)
- Duplicate email at registration → 409 conflict

## Failure Cases
- PUT /api/auth/me without token → 401; with malformed body → 422 flattened detail
- Orphaned user_skills impossible by schema (composite PK + FKs)

## Recovery Procedures
1. Verify row state: sqlite3 skillsynth.db "SELECT * FROM users WHERE email='…';"
2. Re-run auth tests: PYTHONPATH=src python -m pytest tests/test_auth.py -q

## Refactoring Strategy
- If profile editing expands beyond full_name, extend ProfileUpdate deliberately — never widen implicitly
- Consider an explicit email-change flow with re-verification if product requires it
