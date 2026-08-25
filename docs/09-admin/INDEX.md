# SS-EDS: Admin Application

## Purpose
Document the admin application — a completely separate SPA within the Next.js app, with its own layout, navigation, state, permissions model, and feature set. No student features appear in the admin UI.

## Responsibilities
- Provide CRUD interfaces for users, skills, categories, learning paths, resources, job roles
- Implement admin-specific navigation with collapsible sidebar and 11 nav items
- Enforce permission gating: only users with `is_admin=True` can access
- Render analytics dashboard with real-time charts
- Stream audit log via SSE with search and pagination
- Provide system health monitoring and feature flags in settings

## Inputs
- Backend admin router endpoints (via 07-backend)
- Role/permission definitions from database
- SSE event stream for live audit log

## Outputs
- 11 admin pages (dashboard + 10 management pages)
- Admin layout with sidebar, breadcrumbs, and "Switch to Student" link
- Query key factory scoped under `admin` namespace

## Dependencies
- 08-frontend (Next.js App Router, shared components)
- 35-state-management (React Query for admin data)
- 14-security (JWT + admin guard)
- 12-realtime (SSE for audit log)

## Admin Pages
| Route | Page | Description |
|-------|------|-------------|
| `/admin` | Dashboard | System overview, stats, recent activity |
| `/admin/users` | Users | CRUD table, search, pagination |
| `/admin/skills` | Skills | CRUD with difficulty level, icon, color |
| `/admin/categories` | Categories | Tree view with nested categories |
| `/admin/paths` | Paths | CRUD with prerequisite graph |
| `/admin/resources` | Resources | CRUD with type, URL, skill association |
| `/admin/job-roles` | Job Roles | CRUD with skill requirements |
| `/admin/settings` | Settings | Feature flags, system configuration |
| `/admin/audit-log` | Audit Log | SSE-streamed, searchable, paginated |
| `/admin/analytics` | Analytics | Charts: user activity, engagement, health |

## Sequence: Admin CRUD Flow
```
Admin Login → React Query fetches user profile → is_admin check → Redirect to /admin
→ Navigate to page → useQuery fetches data → Render Table → Edit/Create/Delete
→ useMutation → POST/PUT/DELETE API → onSuccess invalidate query key → Table refreshes
```

## State Diagram: Admin Access
```
[Any User] → GET /api/auth/me → is_admin=True? → Yes → /admin renders
                                                ↓  No
                                           Redirect to /dashboard
```

## Layout Structure
```
AdminLayout ('use client')
├── Sidebar (fixed, w-60, collapsible on mobile)
│   ├── Logo + "Admin" badge (rounded bg-primary/10)
│   ├── Nav items (11 icons + labels, active highlight with ChevronRight)
│   └── User section (avatar, name, "Switch to Student" link, Logout)
├── Sticky Header (h-14, border-bottom)
│   └── Mobile hamburger + LocaleSwitcher
└── Main Content (p-6 lg:p-8)
```

## Rules
1. Admin pages are client components (`'use client'`) — interactivity required
2. All admin data fetched via React Query with `admin`-scoped query keys
3. "Switch to Student" link navigates to `/dashboard` — maintains same session
4. Admin sidebar shows 11 items; dashboard is always first, settings is always last
5. No student-specific features (learn, wizard, mastery) appear in admin UI
6. Audit log uses SSE for real-time updates

## Examples
- Admin creates a skill: POST `/api/admin/skills` with name, description, difficulty_level, icon, color
- Audit log entry: `category="admin" action="create" entity_type="skill"` streamed via SSE
- Settings page toggles feature flags like "enable_wizard", "maintenance_mode"

## Edge Cases
- Admin tries to delete own account → blocked by backend
- Role with users assigned → cannot be deleted
- SSE connection lost → audit log auto-reconnects with last event ID

## Failure Cases
- Non-admin user navigates to /admin → redirected, no flash of admin UI
- SSE fails → admin sees stale audit log, retry indicator shown
- Empty admin dashboard → "No data available" state

## Recovery Procedures
1. Check JWT token for `is_admin` claim
2. Clear React Query cache for `['admin']` keys
3. Verify SSE connection in browser DevTools Network tab

## Refactoring Strategy
- Extract admin into dedicated micro-frontend
- Add bulk operations (batch user role update, bulk skills import)
- Implement admin SSE dashboard for real-time system metrics
