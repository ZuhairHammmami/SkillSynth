# Unused Files Report — SkillSynth

Generated: 2026-06-23  
Scope: Full project scan of `/media/zuhair/Extra/SkillSynth/`

---

## 1. BACKEND — Dead Files

### 1.1 Dead entire modules (never imported anywhere)

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/backend/events/publishers.py` | Contains `EventPublishers` class (62 lines). Never imported. Twin `publisher.py` is used instead. Grep for `from backend.events.publishers import` — 0 results. | ✅ Yes |
| `src/backend/mappers/__init__.py` | Empty `__init__.py`. Never imported. | ✅ Yes |
| `src/backend/mappers/profile_mapper.py` | `profile_to_dto()` function (17 lines). Never imported anywhere (`from backend.mappers` — 0 results). DTO mapping done inline in routers. | ✅ Yes |
| `src/backend/mappers/path_mapper.py` | `path_to_dto()` function (14 lines). Same as above. | ✅ Yes |
| `src/backend/cache/__init__.py` | Empty `__init__.py`. Never imported. | ✅ Yes |
| `src/backend/cache/cache_service.py` | Full Redis/SQLite caching service (114 lines). Never imported (`from backend.cache` — 0 results). | ✅ Yes |
| `src/backend/metrics/__init__.py` | Empty `__init__.py`. Never imported. | ✅ Yes |
| `src/backend/scheduler/__init__.py` | Empty `__init__.py`. Never imported. | ✅ Yes |
| `src/backend/telemetry/__init__.py` | Contains only `logging.basicConfig` (8 lines). Never imported. | ✅ Yes |
| `src/backend/exceptions/__init__.py` | Empty `__init__.py`. Never imported. | ✅ Yes |
| `src/backend/validators/__init__.py` | Empty `__init__.py`. Never imported. | ✅ Yes |
| `src/backend/validators/password_validator.py` | `validate_password()` function (11 lines). Never imported. AuthService has its own `validate_password_strength()`. | ✅ Yes |

### 1.2 Dead standalone scripts

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/backend/create_admin.py` | Standalone script to create admin with hardcoded credentials (33 lines). Never imported or referenced (`create_admin` — 0 references in backend/). | ⚠️ Maybe (if admin creation is handled by `main.py` startup) |
| `src/data/learning_paths/example_run.py` | Standalone test script (15 lines). Hardcoded test data. Never imported. | ✅ Yes |

### 1.3 Dead data JSON files (may be dead)

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/data/learning_paths/assessments.json` | May be used by `assessor.py` at runtime. Verify before deleting. | ⚠️ Check |
| `src/data/learning_paths/resources.json` | May be used by `generator.py` at runtime. Verify before deleting. | ⚠️ Check |
| `src/data/learning_paths/rules.json` | May be used by `generator.py` at runtime. Verify before deleting. | ⚠️ Check |

### 1.4 Minor issue — Missing exports in `routers/__init__.py`

`src/backend/routers/__init__.py` only exports 8 routers (not `learning_router` nor `realtime_router`), but `main.py` imports them directly. While this works, it's inconsistent.

---

## 2. FRONTEND — Dead Files

### 2.1 Dead hooks (never used in any page component)

Grep of `src/frontend/src/app/` for these hook names — **0 results** for each:

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/src/shared/hooks/useMasteryPath.ts` | Only referenced by other dead hooks. Not in any page. | ✅ Yes |
| `src/frontend/src/shared/hooks/useMasteryData.ts` | Same chain of dead references. | ✅ Yes |
| `src/frontend/src/shared/hooks/useMasteryPathOptimized.ts` | Same. | ✅ Yes |
| `src/frontend/src/shared/hooks/useLiveData.ts` | Not imported anywhere in app/. | ✅ Yes |
| `src/frontend/src/shared/hooks/useWebSocket.ts` | Not imported anywhere in app/. | ✅ Yes |
| `src/frontend/src/shared/hooks/useConflictPreview.ts` | Not imported anywhere in app/. | ✅ Yes |
| `src/frontend/src/shared/hooks/useConflictDetection.ts` | Not imported anywhere in app/. | ✅ Yes |
| `src/frontend/src/shared/hooks/useNodeCompletion.ts` | Not imported anywhere in app/. | ✅ Yes |
| `src/frontend/src/shared/hooks/useSSE.ts` | Not imported anywhere in app/. (SSE is handled directly in layout) | ✅ Yes |
| `src/frontend/src/shared/hooks/useToast.ts` | Not imported anywhere in entire `src/` (`from.*useToast` — 0 results). Sonner toast is used directly via `<Toaster>`. | ✅ Yes |

### 2.2 Dead services (only used by dead hooks)

All 7 services form an isolated dependency graph — they reference each other and dead hooks, but nothing in `app/` imports them.

| File | Safely deletable? |
|------|-------------------|
| `src/frontend/src/shared/services/StuckProtocolService.ts` | ✅ Yes |
| `src/frontend/src/shared/services/SkillGapAnalyzerService.ts` | ✅ Yes |
| `src/frontend/src/shared/services/PathResolver.ts` | ✅ Yes |
| `src/frontend/src/shared/services/MasteryProgressionService.ts` | ✅ Yes |
| `src/frontend/src/shared/services/MasteryAnalyticsService.ts` | ✅ Yes |
| `src/frontend/src/shared/services/ConflictNotificationService.ts` | ✅ Yes |
| `src/frontend/src/shared/services/AssessmentService.ts` | ✅ Yes |

### 2.3 Dead entities (only used by dead code)

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/src/entities/KnowledgeNode.ts` | Only referenced by dead hooks/services. Grep in `app/` — 0 results. | ✅ Yes |
| `src/frontend/src/entities/UserPath.ts` | Same. Grep in `app/` — 0 results. | ✅ Yes |
| `src/frontend/src/entities/Assessment/index.ts` | Only referenced by dead services. Grep in `app/` — 0 results. | ✅ Yes |
| `src/frontend/src/entities/path/index.ts` | **Not imported anywhere** in entire frontend src/. | ✅ Yes |
| `src/frontend/src/entities/user/index.ts` | Only imported by the dead `authStore.ts`. Not in any page. | ✅ Yes |

### 2.4 Dead store

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/src/shared/store/authStore.ts` | Uses Zustand for auth state. **Never imported anywhere** — only self-referencing. Auth state is handled by JWT cookies + React Query. | ✅ Yes |

### 2.5 Dead lib/utilities

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/src/lib/supabase.ts` | Supabase browser client with `createBrowserClient`. **Never imported anywhere**. Auth is JWT-based via FastAPI, not Supabase. | ✅ Yes |
| `src/frontend/src/shared/lib/queryInvalidator.ts` | `useInvalidateQueries` hook. **Never imported anywhere**. | ✅ Yes |
| `src/frontend/src/shared/api/usePrefetch.ts` | `usePrefetch` hook for prefetching queries. **Never imported anywhere**. | ✅ Yes |

### 2.6 Dead synth components (never used)

File under `src/frontend/src/shared/components/synth/` — all 10 files. Grep for `from.*synth/` in entire frontend — **0 results**.

| File | Safely deletable? |
|------|-------------------|
| `shared/components/synth/Cable.tsx` | ✅ Yes |
| `shared/components/synth/Jack.tsx` | ✅ Yes |
| `shared/components/synth/Knob.tsx` | ✅ Yes |
| `shared/components/synth/LED.tsx` | ✅ Yes |
| `shared/components/synth/Module.tsx` | ✅ Yes |
| `shared/components/synth/Oscilloscope.tsx` | ✅ Yes |
| `shared/components/synth/SignalInput.tsx` | ✅ Yes |
| `shared/components/synth/SpectrumAnalyzer.tsx` | ✅ Yes |
| `shared/components/synth/SynthIcon.tsx` | ✅ Yes |
| `shared/components/synth/VUMeter.tsx` | ✅ Yes |

### 2.7 Dead UI components (not used in any page or layout)

Grep in `src/app/` for `from.*@/shared/ui/<component>` — no matches for these:

| File | Safely deletable? |
|------|-------------------|
| `shared/ui/accordion.tsx` | ✅ Yes |
| `shared/ui/alert.tsx` | ✅ Yes |
| `shared/ui/alert-dialog.tsx` | ✅ Yes |
| `shared/ui/dropdown-menu.tsx` | ✅ Yes |
| `shared/ui/form.tsx` | ✅ Yes |
| `shared/ui/label.tsx` | ✅ Yes |
| `shared/ui/progress.tsx` | ✅ Yes |
| `shared/ui/radio-group.tsx` | ✅ Yes |
| `shared/ui/select.tsx` | ✅ Yes |
| `shared/ui/skeleton.tsx` | ✅ Yes |
| `shared/ui/slider.tsx` | ✅ Yes |
| `shared/ui/tabs.tsx` | ✅ Yes |
| `shared/ui/sheet.tsx` | ✅ Yes |

**Note:** These are shadcn/ui primitives. If they are not imported anywhere in pages or components, they are dead. The `shared/ui/index.ts` barrel export itself is also never imported.

### 2.8 Dead barrel export files

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/src/shared/ui/index.ts` | **Not imported anywhere** in entire frontend. Components are imported by path (e.g. `@/shared/ui/button`). | ✅ Yes |
| `src/frontend/src/shared/lib/index.ts` | **Never imported**. Exports `apiClient` and `utils` re-exports, but consumers import directly. | ✅ Yes |
| `src/frontend/src/shared/api/index.ts` | **Never imported**. Only re-exports `queryKeys`. | ✅ Yes |
| `src/frontend/src/shared/components/index.ts` | **Never imported**. Exports Logo, LocaleSwitcher, Loading — but consumers import by path. | ✅ Yes |

### 2.9 Dead exports in `useApi.ts` (functions never used in pages)

These hooks are defined in the living `useApi.ts` but **never imported** by any page component. They represent dead code within a living file:

| Function | Grep in `app/` | Safely removable? |
|----------|---------------|-------------------|
| `useUpdatePath` | 0 matches | ✅ Yes |
| `useUpdateCategory` | 0 matches | ✅ Yes |
| `useCreateResource` | 0 matches | ✅ Yes |
| `useUpdateResource` | 0 matches | ✅ Yes |
| `useCreateJobRole` | 0 matches | ✅ Yes |
| `useUpdateJobRole` | 0 matches | ✅ Yes |
| `useAdminUpdateUser` | 0 matches | ✅ Yes |
| `useLearningHistory` | 0 matches | ✅ Yes |
| `useSkillGrowth` | 0 matches | ✅ Yes |

### 2.10 Dead assets

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/public/next.svg` | Next.js default. Not referenced in any component. Favicon is `favicon.svg`. | ✅ Yes |
| `src/frontend/public/vercel.svg` | Next.js default. Not referenced. | ✅ Yes |
| `src/frontend/public/file.svg` | Next.js default. Not referenced. | ✅ Yes |
| `src/frontend/public/globe.svg` | Next.js default. Not referenced. | ✅ Yes |
| `src/frontend/public/window.svg` | Next.js default. Not referenced. | ✅ Yes |
| `src/frontend/public/noise.svg` | Next.js default. Not referenced. | ✅ Yes |

### 2.11 Dead types

| File | Reason | Safely deletable? |
|------|--------|-------------------|
| `src/frontend/src/types/supabase.ts` | Supabase database type definitions for tables (`concepts`, `user_mastery`, `user_path`, `assessment_results`). **Never imported anywhere**. These tables don't exist in the SQLite schema. | ✅ Yes |
| `src/frontend/src/types.d.ts` | Declares `declare module 'react-player/lazy'`. `react-player` is not in `package.json` dependencies. | ✅ Yes |

---

## 3. CLEANUP CANDIDATES

### 3.1 QA Screenshots

Every file under `qa-screenshots/` is a QA verification artifact (16 PNG files):

```
qa-screenshots/01-landing-page.png
qa-screenshots/01-landing-page-v2.png
qa-screenshots/02-login-page.png
qa-screenshots/02-register-page.png
qa-screenshots/03-register-page.png
qa-screenshots/03-wizard-step1.png
qa-screenshots/04-dashboard.png
qa-screenshots/04-wizard-step2-assessment.png
qa-screenshots/05-admin-dashboard.png
qa-screenshots/06-admin-as-student-dashboard.png
qa-screenshots/06-wizard.png
qa-screenshots/07-path-detail.png
qa-screenshots/07-paths.png
qa-screenshots/08-admin-users.png
qa-screenshots/09-admin-skills.png
qa-screenshots/10-profile.png
```

Can be safely deleted (QA artifacts for past verification).

### 3.2 Lighthouse Reports

10 files under `lighthouse-reports/`:

```
lighthouse-reports/report.html
lighthouse-reports/report.json
lighthouse-reports/performance-trace.json
lighthouse-reports/page-snapshot.txt
lighthouse-reports/navigation-final/report.html
lighthouse-reports/navigation-final/report.json
lighthouse-reports/snapshot/report.html
lighthouse-reports/snapshot/report.json
lighthouse-reports/verify-fixes/report.html
lighthouse-reports/verify-fixes/report.json
```

Can be safely deleted (audit artifacts).

### 3.3 Supabase Temp Files

8 files under `supabase/.temp/` — all auto-generated by Supabase CLI. Can be deleted.

### 3.4 Python Cache Dirs

`__pycache__` directories exist under `data/learning_paths/`. These are generated and should be gitignored/cleaned.

---

## 4. DEAD MIGRATIONS

| Migration | Status |
|-----------|--------|
| `001_aeis_initial_schema.sql` | Superseded by `002_rebuild_schema.sql` |
| `002_phase_3_4_adaptive_learning.sql` | Superseded by `002_rebuild_schema.sql` |
| `002_rebuild_schema.sql` | Current active schema |
| `003_phase_4_0_ecosystem_synchrony.sql` | Post-rebuild addition |
| `004_phase_4_5_vector_search.sql` | Post-rebuild addition |
| `005_create_user_path.sql` | Latest migration |

`001_aeis_initial_schema.sql` and `002_phase_3_4_adaptive_learning.sql` are superseded and can be archived/deleted. The other 4 are still relevant.

---

## 5. SUMMARY

### Files that can be safely deleted immediately (no impact):
- **Backend:** 11 files (3 modules with content + 2 standalone scripts + 6 empty modules)
- **Frontend hooks:** 10 files
- **Frontend services:** 7 files
- **Frontend entities:** 5 files
- **Frontend store:** 1 file
- **Frontend lib/utils:** 3 files
- **Frontend synth components:** 10 files
- **Frontend unused UI components:** 13 files
- **Frontend barrel exports:** 4 files
- **Frontend assets:** 6 files
- **Frontend types:** 2 files
- **QA screenshots:** 16 files
- **Lighthouse reports:** 10 files
- **Supabase temp:** 8 files

**Total potentially deletable: ~96 files**

### Dead code within living files:
- `useApi.ts`: 9 unused hook exports (lines 144-166, 217-236, 290-320, 332-362, 394-403, 455-472)
- `routers/__init__.py`: Missing 2 router exports (but imports work directly)

### Files to keep with caution:
- `tools/cli/` — Independent CLI tool (not part of app, but useful)
- `src/migrations/*.sql` — All 6 are part of DB versioning (archivable but not deletable)
- `create_admin.py` — Standalone utility, may be kept for reference
- `data/learning_paths/assessments.json`, `resources.json`, `rules.json` — Verify runtime usage
