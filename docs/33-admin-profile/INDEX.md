# SS-EDS: Admin Profile

## Purpose
Document the admin-specific profile features and management capabilities for SkillSynth. Covers admin user creation, role assignment, permission management, and admin-focused UI.

## Responsibilities
- Manage admin user accounts
- Define and assign roles (super_admin, admin, editor, student, content_manager, viewer)
- Control granular permissions per role
- Provide admin-only access to system management features

## Inputs
- Role definitions from seed_all.py
- Permission requirements per feature
- Admin user data

## Outputs
- Admin API endpoints (30+ in admin_router.py)
- Role-based permission gates
- Admin UI components

## Dependencies
- 14-security (RBAC enforcement)
- 09-admin (admin UI pages)
- 10-database (roles table) — ~~profiles.role_id~~ (removed)

## Sequence: Admin User Creation
```
Admin → POST /api/admin/users
  → Validate input
  → Check permissions (require_permission("users:create"))
  → Create profile with is_admin flag
  → Assign role_id (default: "viewer")
  → Create audit log entry
  → Return created user
```

## RBAC Roles (6)
| Role | Key Permissions |
|------|-----------------|
| super_admin | Everything |
| admin | Users/roles/skills/resources CRUD |
| editor | Content creation, path editing |
| student | Learning paths, assessments, own profile |
| content_manager | Resources, assessments |
| viewer | Read-only (stats, reports) |

## State Diagram: Admin Session
```
[Login] → [Admin Dashboard] → [User Management] → [Edit User] → [Save] → [Audit Logged]
                           ↓
                     [Role Management]
                           ↓
                     [System Reports]
```

## ERD References
- roles: name (unique), permissions (JSON string array)
- profiles: ~~role_id FK→roles,~~ is_admin boolean (role_id removed)

## Rules
1. Admin cannot delete own account
2. Roles cannot be deleted if users are assigned
3. Admin auto-grants all permissions regardless of role config
4. Permission check: `require_permission("users:create")` as dependency
5. All admin actions logged to events table with category="audit"

## Examples
- Content Manager can create resources but cannot manage users
- Viewer sees reports but cannot edit any data
- Editor can edit learning paths but cannot assign roles

## Edge Cases
- User assigned multiple roles → not supported (single role per user)
- Super admin removed from system → cannot happen (protected)
- Role permissions changed → existing sessions not affected until re-login

## Failure Cases
- Permission denied on action → 403 with detail message
- Role not found → 404
- Deleting role with users assigned → 409 Conflict

## Recovery Procedures
1. Check roles table for permission definitions
2. ~~Verify profile.role_id is set correctly~~ (role_id removed)
3. Use super_admin account to fix misconfigurations

## Refactoring Strategy
- Add role hierarchy (inheriting permissions from parent roles)
- Implement permission caching for faster auth checks
- Add admin activity log viewer in admin UI
- Support custom role creation (currently 6 fixed roles)
