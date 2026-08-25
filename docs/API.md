# API Reference — DEPRECATED (absorbed into SS-EDS docs/22-api/)

> **⚠️ Gamification endpoints removed:** `/api/gamification/profile`, XP in step complete, achievements.

## Base URL

- **Dev**: `http://127.0.0.1:8000` (FastAPI)
- **Frontend API routes**: `http://localhost:3000/api/*` (Next.js, mostly stubbed)

## Authentication

All protected endpoints require `Authorization: Bearer <token>` header.
Obtain token via `POST /api/auth/token`.

## FastAPI Endpoints (~52)

### Auth — `/api/auth`

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|------------|-------------|
| POST | `/api/auth/register` | No | 5/min | Register (email, password, full_name) |
| POST | `/api/auth/token` | No | 10/min | Login → JWT (OAuth2 form: `username`=email, `password`) |
| GET | `/api/auth/users/me` | JWT | — | Current user profile |
| GET | `/api/auth/me` | JWT | — | Alias for `/users/me` |
| PUT | `/api/auth/users/me` | JWT | — | Update profile (name, skill_profile, preferences) |
| POST | `/api/auth/change-password` | JWT | — | Change password (current_password, new_password) |
| POST | `/api/auth/forgot-password` | No | 3/min | Request reset (email) — alias |
| POST | `/api/auth/request-password-reset` | No | 3/min | Request reset (email) |
| POST | `/api/auth/reset-password` | No | 3/min | Reset with token |
| POST | `/api/auth/sse-token` | JWT | — | Get short-lived SSE token (5min) |

### Wizard — `/api`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/wizard-options` | No | Job roles, career fields grouped, format/language preferences |

### Assessments — `/api`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/assessments/{job_role_title}` | No | Assessment questions for a job role |
| POST | `/api/assessment-results` | JWT | Submit answers → score + skill profile update |

### Paths — `/api`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/generate-path/` | JWT | Generate learning path (goal, answers, weekly_hours, preferences) |
| GET | `/api/paths/` | JWT | List all user's paths |
| GET | `/api/paths/{path_id}` | JWT | Path detail with steps, resources, completion status |
| DELETE | `/api/paths/{path_id}` | JWT | Delete path + steps (cascade) |
| PUT | `/api/paths/{path_id}` | JWT | Update title/description/skill_ids |
| PUT | `/api/paths/{path_id}/skills` | JWT | Update skill_ids only |
| POST | `/api/paths/{path_id}/regenerate` | JWT | Regenerate steps |
| GET | `/api/paths/{path_id}/analytics` | JWT | Path completion analytics |

### Progress & Gamification — `/api`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/steps/{step_id}/complete` | JWT | Complete step (+10 XP, update streak, check achievements) |
| POST | `/api/steps/{step_id}/undo-complete` | JWT | Undo completion (-10 XP) |
| GET | `/api/progress/dashboard` | JWT | Aggregated progress + gamification |
| GET | `/api/gamification/profile` | JWT | XP, level, streak, achievements |

### Analytics — `/api/analytics`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/analytics/dashboard` | JWT | All analytics aggregated |
| GET | `/api/analytics/path-progress/{path_id}` | JWT | Per-path step-by-step progress |
| GET | `/api/analytics/skill-growth` | JWT | Skill proficiency breakdown + gaps |
| GET | `/api/analytics/learning-history` | JWT | Last 20 completions + 7-day daily activity |
| GET | `/api/analytics/learning-velocity` | JWT | Weekly/monthly velocity |

### Admin — `/api/admin` (all require admin JWT)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/admin/users` | List users (paginated: skip, limit) |
| POST | `/api/admin/users` | Create user |
| PUT | `/api/admin/users/{user_id}` | Update user |
| DELETE | `/api/admin/users/{user_id}` | Delete user (cannot delete self) |
| GET/POST/PUT/DELETE | `/api/admin/roles[/{role_id}]` | CRUD roles (delete blocked if users assigned) |
| GET/POST/PUT/DELETE | `/api/admin/skills[/{skill_id}]` | CRUD skills |
| GET/POST/PUT/DELETE | `/api/admin/categories[/{category_id}]` | CRUD categories |
| GET/POST/PUT/DELETE | `/api/admin/resources[/{resource_id}]` | CRUD resources |
| GET/POST/PUT/DELETE | `/api/admin/job-roles[/{job_role_id}]` | CRUD job roles |
| GET | `/api/admin/audit-log` | Paginated audit log |
| GET | `/api/admin/analytics/overview` | 7-day admin analytics |
| GET | `/api/admin/reports/user-activity` | Users stats |
| GET | `/api/admin/reports/content-engagement` | Content stats |
| GET | `/api/admin/reports/system-health` | System status |
| GET | `/api/admin/reports/most-active-users` | Top 10 users |
| GET | `/api/admin/reports/most-requested-skills` | Top skills |
| GET | `/api/admin/reports/aggregated` | All reports |

### Real-time

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/events` | JWT | SSE stream (step/assessment/path events) |

## Next.js API Routes (Frontend)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | `/api/ingest` | AEIS knowledge ingestion | Mock |
| POST | `/api/mastery/explain` | LLM concept explanation | Semi-real |
| POST | `/api/mastery/progress` | Update user mastery | Mock |
| GET | `/api/mastery/user-path` | Fetch/init mastery record | Mock |
| GET | `/api/mastery/assessment/generate` | Generate assessment | Uses AssessmentService |
| POST | `/api/mastery/assessment/submit` | Submit & grade assessment | Mock |
| POST | `/api/projects/submit` | Submit project work | Mock |
| GET | `/api/search/discover` | Semantic search | Mock/fallback |

## SSE Events

Events streamed to `/api/events`:
- `step_completed` — `{profile_id, step_id, path_id, xp_awarded}`
- `step_reverted` — `{profile_id, step_id, path_id, xp_deducted}`
- `path_regenerated` — `{path_id}`
- `assessment_completed` — `{profile_id, assessment_id, score}`
