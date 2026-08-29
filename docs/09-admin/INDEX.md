# SS-EDS: Admin Application

## Purpose
Document the standalone admin application at `src/admin-app` (:3001) — a separate Next.js app (English-only, own layout and navigation) providing full CRUD over platform content plus operational tooling. No student features exist here.

## Responsibilities
- Provide CRUD interfaces with create/edit dialogs for users, skills, categories, resources, job roles, assessments
- Enforce access via the binary `users.is_admin` flag (AdminGuard; no roles/permissions UI)
- Surface restricted-delete flows (409 dependency census → force-delete confirmation)
- Provide reports, system health, backups, DB inspector, audit logs, and read-only System Configuration

## Inputs
- Backend admin endpoints `/api/admin/*` (30 operations, require_admin-gated)
- SSE admin channel for the audit feed
- JWT of an `is_admin=True` user

## Outputs
- 16 pages (see table below), sidebar navigation with 15 items
- Query keys scoped under an admin namespace for cache isolation

## Dependencies
- 07-backend (admin.py + catalog_admin.py routers)
- 14-security (JWT + is_admin gate)
- 12-realtime / 23-events (SSE audit stream)

## Admin Pages
| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | Dashboard | Overview stats and recent activity |
| `/users` | Users | CRUD table + edit dialog, lock/unlock actions |
| `/categories` | Categories | Tree CRUD with parent-cycle rejection feedback |
| `/skills` | Skills | CRUD incl. prerequisites; delete shows dependency census |
| `/resources` | Resources | CRUD with type/URL/skill association |
| `/job-roles` | Job Roles | CRUD incl. skill weightings |
| `/assessments` | Assessments | List + delete (restricted) |
| `/paths` | Paths | Read-only management view |
| `/reports` | Reports | Aggregated + system-health report views |
| `/health` | System Health | GET /api/admin/reports/system-health rendering |
| `/settings` | Settings | Change-password + account settings |
| `/audit-logs` | Audit Logs | activity_log feed (SSE-backed) |
| `/backups` | Backups | List/create database backups |
| `/db-inspector` | DB Inspector | Table/row browser over the live schema |
| `/feature-flags` | System Configuration | AI enable/disable toggle + runtime config view (writable) |

## Sequence: Admin CRUD Flow
```
Login → GET /api/auth/me → is_admin? → AdminGuard passes → page loads
→ useQuery fetch → table render → Create/Edit dialog → mutation (POST/PUT)
→ onSuccess invalidates query key → table refreshes
Delete → 409 census? → confirm dialog → DELETE ?force=true → refresh
```

## State Diagram: Admin Access
```
[Request] → token valid? ──no──→ /login
                ↓ yes
          is_admin=True? ──no──→ redirect (student app / error)
                ↓ yes
           [Dashboard renders]
```

## Layout Structure
```
AdminLayout (English-only)
├── Fixed sidebar — logo, 15 nav items, active highlight
├── Sticky header (h-14) with page context
└── Main content area (p-6 lg:p-8)
```

## Rules
1. Pages are client components; all data via React Query with admin-scoped keys
2. Access control is only `is_admin` — there is no role picker or permission matrix in the UI
3. Deletes that return 409 present the dependency census and offer explicit force-delete (`?force=true`, ADR-014)
4. English-only copy; design tokens match the student frontend's Linear/Notion style
5. The admin app runs on :3001 and never imports code from `src/frontend`

## Examples
- Edit a skill name → PUT /api/admin/skills/{id} → case-insensitive uniqueness enforced; duplicate returns 409
- Delete a category with children → 409 + census list → confirm → DELETE with `?force=true`

## Edge Cases
- Non-admin JWT reaching /api/admin/* → backend 403 regardless of UI state
- SSE drop while viewing audit logs → feed resumes on EventSource auto-reconnect

## Failure Cases
- Expired token mid-session → queries fail with 401 → re-login required
- Empty datasets → pages render explicit empty states

## Recovery Procedures
1. Re-authenticate to mint a fresh 24h token
2. Clear React Query cache (`['admin']` namespace) after auth changes

## Refactoring Strategy
- New admin capability = new page + api module mirroring a new /api/admin endpoint group
- Keep dialogs generic; reuse the census/force-delete pattern for any new restricted delete
