# SS-EDS: Admin Profile

## Purpose
Document admin identity and authorization. There is exactly one privilege class: `users.is_admin = true`. No roles table, no permission strings, no per-role dependencies — the require_admin policy is the entire gate.

## Responsibilities
- Gate all /api/admin/* endpoints via policies (require_admin dependency)
- Auto-create the bootstrap admin at startup when ADMIN_PASSWORD is set (main.py lifespan)
- Provide the admin app (:3001) its session and data surface

## Inputs
- users.is_admin boolean on every JWT
- Env vars ADMIN_EMAIL / ADMIN_PASSWORD (bootstrap, optional)
- Admin limiter: 60/min on /api/admin/* (limiter.py)

## Outputs
- 30 admin operations across 19 paths (see 22-api for the inventory)
- Admin SSE channel GET /api/realtime/admin/events (?category= filter)

## Dependencies
- 14-security (JWT verification, lockout applies to admins equally)
- 09-admin (admin app pages)
- 10-database (users; activity_log audit trail)

## Authorization Model
```
Request → get_current_user (validates JWT) → require_admin (checks is_admin)
  → pass: handler runs        → fail: 403
```
| Class | Capability |
|-------|-----------|
| is_admin = true | Full admin API + admin app + admin SSE channel |
| is_admin = false | Student API only; admin calls return 403 |

## Sequence: Bootstrap Admin Creation
```
python run.py → lifespan startup
  → ADMIN_EMAIL + ADMIN_PASSWORD set?
    → create user with is_admin=true if email not present (idempotent)
  → [Ready]
Seeded accounts: admin@skillsynth.io / demo / editor / veteran / student2 (seed_v3.py)
```

## State Diagram: Admin Session
```
[Login] → [Dashboard] → Users · Skills · Categories · Job Roles · Resources
                      → Assessments · Paths · Backups · DB Inspector
                      → Feature Flags · Reports · Health · Settings · Audit Logs
Every mutation → activity_log entry (admin events feed GET /api/admin/events)
```

## ERD References
- users.is_admin (boolean, NOT NULL, default false) — the only authorization column in the schema

## Rules
1. An admin cannot delete their own account (admin_service returns "Cannot delete yourself"; router maps it to 400)
2. An admin cannot demote their own account (admin_service.py:60 guard)
3. Granting/revoking admin is a PUT /api/admin/users/{id} field edit by an existing admin
4. Lockout policy is identical for admins: 5 failed logins → 15-minute lock
5. Every admin mutation writes an activity_log row with actor and payload summary

## Examples
- Non-admin calls DELETE /api/admin/skills/12 → 403 before any service logic runs
- Admin renames a skill to a case-duplicate → 409 uniqueness conflict

## Edge Cases
- Self-demotion is always rejected, preventing an accidental single-admin lockdown
- Bootstrap admin skipped when ADMIN_PASSWORD unset (seeded admin remains)

## Failure Cases
- Expired token (>24h) on admin route → 401; re-login required
- require_admin failure → 403 with no enumeration detail

## Recovery Procedures
1. Lost admin access → set ADMIN_EMAIL/ADMIN_PASSWORD and restart; the account is re-created/upgraded at boot
2. Audit actions: GET /api/admin/events or the Audit Logs page in :3001

## Refactoring Strategy
- Keep the binary model until a concrete need proves finer granularity; any change requires an ADR superseding ADR-013's rationale
