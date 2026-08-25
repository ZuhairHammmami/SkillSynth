# Large Files Report — SkillSynth

## Summary

| Category | Files Scanned | > 150 lines | > 300 lines | Target < 150 |
|----------|:---:|:---:|:---:|:---:|
| Backend Python | 67 | 8 | 1 | 59 |
| Frontend TS/TSX | ~100 | 17 | 4 | ~83 |
| Root scripts | 4 | 2 | 0 | 2 |
| SQL migrations | 6 | 3 | 2 | 3 |

---

## Table of Files > 150 Lines

### Backend (Python)

| File | Lines | Responsibilities | Split Priority |
|------|-------|------------------|:---:|
| `src/backend/routers/admin_router.py` | 300 | Reports (4), Users CRUD (3), Roles CRUD (4), Skills CRUD (3), Categories CRUD (3), Resources CRUD (3), Job Roles CRUD (3), Audit/Events (3), Analytics (1) | **HIGH** |
| `src/backend/routers/paths_router.py` | 200 | Generate path, List paths, Get path detail, Update path, Delete path, Update skills, Regenerate path, Path analytics | **MED** |
| `src/backend/main.py` | 172 | App factory, CORS, middlewares, exception handlers, SSE endpoint, startup hook | LOW |
| `src/backend/routers/learning_router.py` | 171 | Knowledge graph, Generate path, Analysis, Recommendations, Progress, Time estimate, Skill gaps | **MED** |
| `src/backend/services/auth_service.py` | 164 | Password hashing, JWT creation/rotation/decode, Login lockout, Password validation, Token management | **MED** |
| `src/backend/routers/realtime_router.py` | 161 | SSE endpoint, Notification push, Admin broadcast, WebSocket handler, WS connection tracking | **MED** |
| `src/backend/services/analytics_service.py` | 153 | Dashboard stats, Path progress, Skill growth, Learning history, Learning velocity | LOW |
| `src/backend/routers/auth_router.py` | 150 | Register, Login, Profile (CRUD), SSE token, Change password, Forgot/reset password | LOW |

### Root Scripts

| File | Lines | Responsibilities | Split Priority |
|------|-------|------------------|:---:|
| `seed_all.py` | 968 | Massive monolithic seed — creates all 32 tables' data in one file | **HIGH** |
| `seed_v2.py` | 845 | Alternative seed — similar scope, slightly smaller | **HIGH** |

### Frontend — TypeScript/TSX (≥ 150 lines)

| File | Lines | Responsibilities | Split Priority |
|------|-------|------------------|:---:|
| `shared/hooks/useApi.ts` | 483 | 30+ React Query hooks for all API endpoints — auth, profile, paths, admin CRUD, analytics — monolithic hook factory | **HIGH** |
| `shared/services/AssessmentService.ts` | 439 | Assessment generation, question templates (7 types), validation, adaptive difficulty, skip logic | **HIGH** |
| `shared/hooks/useMasteryData.ts` | 319 | User mastery query, Concepts query (mock data), Analytics query, Complete node mutation, Prefetch utilities | **HIGH** |
| `shared/services/PathResolver.ts` | 318 | DAG node building, topological layering, BFS shortest path, time estimation, path validation, JSON export | **HIGH** |
| `shared/services/ConflictNotificationService.ts` | 283 | Node access check, skill override validation, blocked nodes, conflict/override/blocked notifications, toast integration | MED |
| `shared/services/MasteryProgressionService.ts` | 282 | Node completion flow, DAG recalculation, persistence, newly accessible node detection, completion stats | MED |
| `types/api.ts` | 263 | 20+ TypeScript interfaces — all API response/request types | LOW |
| `shared/services/StuckProtocolService.ts` | 256 | Stuck detection, intervention options, simplified subpath, intervention records, tracking init, effectiveness assessment | MED |
| `shared/services/SkillGapAnalyzerService.ts` | 255 | Gap analysis, weak skill detection, priority scoring, recommendations, prerequisite review | MED |
| `shared/components/synth/SynthIcon.tsx` | 222 | 25 SVG icon components + barrel export — purely declarative SVG | LOW |
| `app/page.tsx` | 212 | Landing page (header, hero, features, stats, how-it-works, testimonials, CTA, footer) | LOW |
| `entities/Assessment/index.ts` | 209 | 8 type definitions + 8 Zod schemas for assessment entities | LOW |
| `shared/ui/select.tsx` | 208 | 12 Radix select sub-components + inline SVG icons — generated shadcn boilerplate | LOW |
| `shared/services/MasteryAnalyticsService.ts` | 178 | MasteryMetrics interface, coverage/velocity/time-series/category distribution/estimation | LOW |
| `app/(student)/learn/page.tsx` | 170 | Learn page (path list, generation dialog, search/filter) | LOW |
| `shared/ui/form.tsx` | 167 | Form context/wrapper, 6 sub-components — generated shadcn boilerplate | LOW |
| `types/supabase.ts` | 158 | Supabase database type definitions for 4 tables | LOW |

### Migrations (SQL)

| File | Lines | Responsibilities |
|------|-------|------------------|
| `src/migrations/002_rebuild_schema.sql` | 568 | Full schema rebuild — all 32 tables, indexes, constraints |
| `src/migrations/003_phase_4_0_ecosystem_synchrony.sql` | 307 | Phase 4 additions — ecosystem tables, relationships |
| `src/migrations/004_phase_4_5_vector_search.sql` | 211 | Vector search setup — FTS indexes, embeddings table |

---

## Priority Split Plan — Files > 300 Lines (Detailed)

### 1. `src/backend/routers/admin_router.py` (300 lines)

**Problem**: Single file handles 8 distinct CRUD domains + reports + events + analytics.

**Split plan**:

| New File | Responsibilities | Est. Lines |
|----------|-----------------|:---:|
| `routers/admin_reports_router.py` | Reports (user-activity, content-engagement, system-health, most-active-users, most-requested-skills, aggregated) | ~50 |
| `routers/admin_users_router.py` | Users CRUD (list, create, update, delete) | ~60 |
| `routers/admin_roles_router.py` | Roles CRUD (list, create, update, delete) | ~60 |
| `routers/admin_skills_router.py` | Skills CRUD (list, create, update, delete) | ~50 |
| `routers/admin_categories_router.py` | Categories CRUD | ~40 |
| `routers/admin_resources_router.py` | Resources CRUD | ~40 |
| `routers/admin_job_roles_router.py` | Job Roles CRUD | ~50 |
| `routers/admin_events_router.py` | Audit log, events list, events stream | ~50 |
| `routers/admin_analytics_router.py` | Analytics overview | ~20 |

**Update `main.py`**: Replace single import with 9 new router imports.

---

### 2. `src/frontend/src/shared/hooks/useApi.ts` (483 lines)

**Problem**: 30+ hooks all in one file. Each hook is a tiny `useQuery`/`useMutation` wrapper — they should be co-located with their domain.

**Split plan**:

| New File | Responsibilities | Est. Lines |
|----------|-----------------|:---:|
| `shared/hooks/useAuthApi.ts` | `useAuth`, `useProfile`, `useUpdateProfile`, `useChangePassword`, `useForgotPassword`, `useResetPassword` | ~60 |
| `shared/hooks/usePathApi.ts` | `usePaths`, `usePathDetail`, `useGeneratePath`, `useUpdatePath`, `useDeletePath`, `useCompleteStep`, `useUndoCompleteStep` | ~80 |
| `shared/hooks/useAdminApi.ts` | `useAdminDashboard`, `useAdminUsers`, `useAdminDeleteUser`, `useAdminUpdateUser`, `useAdminPaths` | ~50 |
| `shared/hooks/useSkillApi.ts` | `useSkills`, `useCreateSkill`, `useUpdateSkill`, `useDeleteSkill` | ~50 |
| `shared/hooks/useCategoryApi.ts` | `useCategories`, `useCreateCategory`, `useUpdateCategory`, `useDeleteCategory` | ~50 |
| `shared/hooks/useResourceApi.ts` | `useResources`, `useCreateResource`, `useUpdateResource`, `useDeleteResource` | ~50 |
| `shared/hooks/useJobRoleApi.ts` | `useJobRoles`, `useCreateJobRole`, `useUpdateJobRole`, `useDeleteJobRole` | ~50 |
| `shared/hooks/useAnalyticsApi.ts` | `useAnalyticsDashboard`, `useLearningHistory`, `useSkillGrowth` | ~40 |
| `shared/hooks/useSystemApi.ts` | `useAuditLog`, `useAdminAnalytics`, `useRoles`, `useWizardOptions` | ~50 |

**Quick win**: Extract `const TOKEN_COOKIE = 'authToken'` to a shared constants file.

---

### 3. `src/frontend/src/shared/services/AssessmentService.ts` (439 lines)

**Problem**: 7 question generator methods (definition, application, comparison, scenario, code, true/false, multi-concept) plus validation + adaptive difficulty + skip check all in one class.

**Split plan**:

| New File | Responsibilities | Est. Lines |
|----------|-----------------|:---:|
| `shared/services/assessment/generateAssessment.ts` | `generateAssessment()` — orchestrates question generation, builds Assessment object | ~50 |
| `shared/services/assessment/questionTemplates.ts` | 7 `create*Question()` functions extracted as pure functions | ~150 |
| `shared/services/assessment/validateAssessment.ts` | `validateAssessment()` — grading, score calculation, feedback | ~60 |
| `shared/services/assessment/adaptiveDifficulty.ts` | `calculateAdaptiveDifficulty()`, `canSkipAssessment()` | ~40 |
| `shared/services/assessment/types.ts` | Interfaces: `AssessmentGenerationOptions`, `AssessmentValidationResult` | ~30 |

**Quick win**: Extract question template content (definition map, static options) into a `questionData.ts` constants file.

---

### 4. `src/frontend/src/shared/hooks/useMasteryData.ts` (319 lines)

**Problem**: 6 hooks/utilities in one file including mock data duplication, plus inline `fetchUserMastery` and prefetch helpers.

**Split plan**:

| New File | Responsibilities | Est. Lines |
|----------|-----------------|:---:|
| `shared/hooks/useUserMastery.ts` | `useUserMastery()` — fetch hook only | ~50 |
| `shared/hooks/useConcepts.ts` | `useConcepts()` — fetch/mock concepts hook | ~60 |
| `shared/hooks/useMasteryAnalytics.ts` | `useMasteryAnalytics()` — analytics query | ~30 |
| `shared/hooks/useCompleteNode.ts` | `useCompleteNodeMutation()` | ~50 |
| `shared/hooks/usePrefetchMastery.ts` | `usePrefetchMasteryData()` + `fetchUserMastery()` helper | ~80 |

**Quick win**: Extract mock concept data to a `data/mockConcepts.ts` constants file (currently duplicated between `useConcepts` and `prefetchConcepts`).

---

### 5. `src/frontend/src/shared/services/PathResolver.ts` (318 lines)

**Problem**: DAG building, layer computation, shortest path (BFS), time estimation, path validation, and JSON export all in one class.

**Split plan**:

| New File | Responsibilities | Est. Lines |
|----------|-----------------|:---:|
| `shared/services/path-resolver/dagBuilder.ts` | `buildDAGNodes()` — constructs DAG from concepts | ~60 |
| `shared/services/path-resolver/layerComputer.ts` | `computeLayers()` — topological sort into layers | ~50 |
| `shared/services/path-resolver/shortestPath.ts` | `calculateShortestPath()` — BFS algorithm | ~60 |
| `shared/services/path-resolver/estimator.ts` | `estimateTimeToMastery()` — time heuristics | ~30 |
| `shared/services/path-resolver/validator.ts` | `validatePath()` — prerequisite validation | ~30 |
| `shared/services/path-resolver/serializer.ts` | `exportDAGAsJSON()` — JSON formatting | ~30 |
| `shared/services/path-resolver/types.ts` | `DAGNode`, `LearningPathDAG`, `PathResolverResult` interfaces | ~40 |
| `shared/services/path-resolver/index.ts` | `PathResolverService` that orchestrates all parts | ~60 |

---

### 6. Root Scripts — `seed_all.py` (968) + `seed_v2.py` (845)

**Problem**: Monolithic seed files contain all 32 tables' seed data in sequence.

**Split plan**:

| New File | Responsibilities |
|----------|-----------------|
| `seed/seed_users.py` | Admin, demo, editor, veteran, student users |
| `seed/seed_categories.py` | All categories |
| `seed/seed_skills.py` | All skills + prerequisites |
| `seed/seed_resources.py` | All resources |
| `seed/seed_job_roles.py` | Job roles + skill links |
| `seed/seed_paths.py` | Paths + steps |
| `seed/seed_assessments.py` | Assessments + results |
| `seed/seed_events.py` | Events/logs |
| `seed/seed_mastery.py` | Mastery progress data |
| `seed/seed_all.py` | Orchestrator — imports and runs all seed modules in order |

---

### 7. Migrations — `002_rebuild_schema.sql` (568 lines) + `003_phase_4_0_ecosystem_synchrony.sql` (307 lines)

**Problem**: SQL files are large but this is expected for schema definitions. However, they can be split by domain.

**Split plan**:

| New File | Table Groups |
|----------|-------------|
| `migrations/002a_core_tables.sql` | profile, role, category, skill, resource |
| `migrations/002b_path_tables.sql` | path, path_step, path_skill, step_completion |
| `migrations/002c_assessment_tables.sql` | assessment, assessment_result, assessment_question |
| `migrations/002d_analytics_tables.sql` | event, event_log, analytics_snapshot |
| `migrations/002e_learning_tables.sql` | learning_path, mastery_tracking, skill_gap |
| `migrations/003a_ecosystem_tables.sql` | Phase 4 ecosystem additions |

---

## Quick Wins (Extract Constants, Types, Utilities)

### Backend
| File | Quick Win |
|------|-----------|
| `admin_router.py` | Extract magic strings (`"user.create"`, `"user.delete"`, etc.) to `constants/audit_actions.py` |
| `paths_router.py` | Extract resource creation logic in `regenerate_path` to `ResourceService.create_or_get()` |
| `auth_service.py` | Extract `_login_attempts` dict to a dedicated `LoginTracker` class in `services/login_tracker.py` |
| `analytics_service.py` | Extract XP level calculation (`level * 100` loop) to utility function |

### Frontend
| File | Quick Win |
|------|-----------|
| `useApi.ts` | Extract `TOKEN_COOKIE` constant, create `useApiKeys.ts` for query key constants |
| `useMasteryData.ts` | Extract mock concept data to `data/mockConcepts.ts` (duplicated twice) |
| `SynthIcon.tsx` | Each icon component is already small — barrel export is fine, but inline SVG duplication could be reduced |
| `Assessment/index.ts` | Already good — types + schemas together is fine at 209 lines |

---

## Files Already Compliant (< 150 Lines)

### Backend (59 files) — all Clean Architecture layers
| Layer | Count | Examples |
|-------|:-----:|----------|
| `entities/` | 8 | `skill.py (31)`, `assessment.py (32)`, `profile.py (32)`, `path.py (64)` |
| `repositories/` | 10 | `generic_repository.py (42)`, `skill_repository.py (67)`, etc. |
| `dto/` | 10 | `category.py (39)`, `resource.py (68)`, `path.py (76)`, etc. |
| `services/` | 8 | `event_service.py (25)`, `email_service.py (45)`, `sse_service.py (102)`, etc. |
| `routers/` | 4 | `options_router.py (33)`, `analytics_router.py (37)`, `assessments_router.py (38)`, `problems_router.py (40)` |
| `middlewares/` | 3 | `security.py (57)`, `csrf.py (45)`, `compression.py (38)` |
| `policies/` | 1 | `auth_policy.py (57)` |
| `commands/` | 1 | `learning_commands.py (111)` |
| `queries/` | 1 | `learning_queries.py (116)` |
| `cache/` | 1 | `cache_service.py (114)` |
| `events/` | 2 | `publishers.py (62)`, `publisher.py (65)` |
| `config/` | 1 | `app_settings.py (32)` |

### Frontend (most files < 150)
| Category | Count | Examples |
|----------|:-----:|----------|
| `shared/ui/` | ~15 | `button.tsx (53)`, `card.tsx (50)`, `badge.tsx (32)` |
| `app/*/` | ~20 | `dashboard/page.tsx (140)`, `profile/page.tsx (108)` |
| `shared/hooks/` | ~4 | `useToast.ts (41)`, `useLiveData.ts (66)`, `useWebSocket.ts (119)` |
| `entities/` | 3 | `user/index.ts (34)`, `path/index.ts (55)`, `KnowledgeNode.ts (133)` |

---

## Recommended Split Order

| Priority | File | Lines | Reason |
|:--------:|------|:-----:|--------|
| 1 | `seed_all.py` | 968 | Largest file, blocks seeding maintenance |
| 2 | `seed_v2.py` | 845 | Same problem as seed_all |
| 3 | `useApi.ts` | 483 | Most imported hook file — affects all pages |
| 4 | `AssessmentService.ts` | 439 | Core assessment logic — hard to maintain |
| 5 | `useMasteryData.ts` | 319 | Mock data duplication, mixed concerns |
| 6 | `PathResolver.ts` | 318 | Algorithm-heavy, each method is independently testable |
| 7 | `admin_router.py` | 300 | Only backend file over 300 — violates Clean Architecture |
| 8 | Migrations (568, 307) | 568 | Domain-split improves clarity |
| 9 | 150-300 line files | 153-283 | Lower urgency but still benefit from extraction |

---

## Per-File Line Count Compliance Rules

| Rule | Applies To |
|------|------------|
| **< 150 lines** — target state for all files | All backend Python + frontend TS/TSX |
| **OK at 150-200** — if single-responsibility | R outers, shadcn UI wrappers, page components |
| **Must split** — > 300 | All 8 files identified above |

Total files inspected: **177+** across backend, frontend, scripts, and migrations.
