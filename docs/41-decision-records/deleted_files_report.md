# Deleted Files Report — SkillSynth Cleanup

Generated: 2026-06-23  
Source: `unused_files_report.md` — Phase 6 cleanup

---

## Successfully Deleted (83 files)

### Group 1 — Backend Dead Files (14 files)
| File | Reason |
|------|--------|
| `src/backend/events/publishers.py` | Twin `publisher.py` used instead |
| `src/backend/mappers/__init__.py` | Empty init, never imported |
| `src/backend/mappers/profile_mapper.py` | Never imported; DTO mapping done inline |
| `src/backend/mappers/path_mapper.py` | Never imported; DTO mapping done inline |
| `src/backend/cache/__init__.py` | Empty init, never imported |
| `src/backend/cache/cache_service.py` | Full caching service, never imported |
| `src/backend/metrics/__init__.py` | Empty init, never imported |
| `src/backend/scheduler/__init__.py` | Empty init, never imported |
| `src/backend/telemetry/__init__.py` | Only `logging.basicConfig`, never imported |
| `src/backend/exceptions/__init__.py` | Empty init, never imported |
| `src/backend/validators/__init__.py` | Empty init, never imported |
| `src/backend/validators/password_validator.py` | Never imported; AuthService has own validation |
| `src/backend/create_admin.py` | Standalone script; admin creation handled by `main.py` |
| `src/data/learning_paths/example_run.py` | Standalone test script, never imported |

### Group 2 — Frontend Dead Hooks (10 files)
| File | Reason |
|------|--------|
| `src/frontend/src/shared/hooks/useToast.ts` | Not imported anywhere; Sonner used directly |
| `src/frontend/src/shared/hooks/useSSE.ts` | Not imported; SSE handled directly in layout |
| `src/frontend/src/shared/hooks/useLiveData.ts` | Not imported in any page |
| `src/frontend/src/shared/hooks/useWebSocket.ts` | Not imported in any page |
| `src/frontend/src/shared/hooks/useConflictPreview.ts` | Not imported in any page |
| `src/frontend/src/shared/hooks/useConflictDetection.ts` | Not imported in any page |
| `src/frontend/src/shared/hooks/useNodeCompletion.ts` | Not imported in any page |
| `src/frontend/src/shared/hooks/useMasteryPath.ts` | Only imported by other dead hooks |
| `src/frontend/src/shared/hooks/useMasteryData.ts` | Only imported by other dead hooks |
| `src/frontend/src/shared/hooks/useMasteryPathOptimized.ts` | Only imported by other dead hooks |

### Group 3 — Frontend Dead Services (7 files)
| File | Reason |
|------|--------|
| `src/frontend/src/shared/services/StuckProtocolService.ts` | Only used by dead hooks |
| `src/frontend/src/shared/services/SkillGapAnalyzerService.ts` | Only used by dead hooks |
| `src/frontend/src/shared/services/PathResolver.ts` | Only used by dead hooks |
| `src/frontend/src/shared/services/MasteryProgressionService.ts` | Only used by dead hooks |
| `src/frontend/src/shared/services/MasteryAnalyticsService.ts` | Only used by dead hooks |
| `src/frontend/src/shared/services/ConflictNotificationService.ts` | Only used by dead hooks |
| `src/frontend/src/shared/services/AssessmentService.ts` | Only used by dead hooks |

### Group 4 — Frontend Dead Entities (2 files — 3 others restored)
| File | Reason |
|------|--------|
| `src/frontend/src/entities/path/index.ts` | Not imported anywhere |
| `src/frontend/src/entities/user/index.ts` | Only imported by dead `authStore.ts` |

### Group 5 — Frontend Store + Lib (4 files)
| File | Reason |
|------|--------|
| `src/frontend/src/shared/store/authStore.ts` | Never imported; JWT cookies + React Query used |
| `src/frontend/src/lib/supabase.ts` | Never imported; auth is JWT-based via FastAPI |
| `src/frontend/src/shared/lib/queryInvalidator.ts` | Never imported |
| `src/frontend/src/shared/api/usePrefetch.ts` | Never imported |

### Group 6 — Synth Components (10 files)
| File | Reason |
|------|--------|
| `src/frontend/src/shared/components/synth/Cable.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/Jack.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/Knob.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/LED.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/Module.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/Oscilloscope.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/SignalInput.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/SpectrumAnalyzer.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/SynthIcon.tsx` | Never imported |
| `src/frontend/src/shared/components/synth/VUMeter.tsx` | Never imported |

### Group 7 — Dead UI Components (13 files)
| File | Reason |
|------|--------|
| `src/frontend/src/shared/ui/accordion.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/alert.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/alert-dialog.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/dropdown-menu.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/form.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/label.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/progress.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/radio-group.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/select.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/skeleton.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/slider.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/tabs.tsx` | Not imported in any page |
| `src/frontend/src/shared/ui/sheet.tsx` | Not imported in any page |

### Group 8 — Barrel Exports (4 files)
| File | Reason |
|------|--------|
| `src/frontend/src/shared/ui/index.ts` | Never imported; components imported by path |
| `src/frontend/src/shared/lib/index.ts` | Never imported |
| `src/frontend/src/shared/api/index.ts` | Never imported |
| `src/frontend/src/shared/components/index.ts` | Never imported |

### Group 9 — Assets (6 files)
| File | Reason |
|------|--------|
| `src/frontend/public/next.svg` | Next.js default; not referenced |
| `src/frontend/public/vercel.svg` | Next.js default; not referenced |
| `src/frontend/public/file.svg` | Next.js default; not referenced |
| `src/frontend/public/globe.svg` | Next.js default; not referenced |
| `src/frontend/public/window.svg` | Next.js default; not referenced |
| `src/frontend/public/noise.svg` | Next.js default; not referenced |

### Group 10 — Types (2 files)
| File | Reason |
|------|--------|
| `src/frontend/src/types.d.ts` | Only `declare module 'react-player/lazy'`; react-player not in deps |
| `src/frontend/src/types/supabase.ts` | Supabase types; tables don't exist in SQLite schema |

### Group 11 — QA/Lighthouse (26 files)
| Path | Reason |
|------|--------|
| `qa-screenshots/` (16 PNG files) | QA verification artifacts |
| `lighthouse-reports/` (10 files) | Audit artifacts |

### Group 12 — Supabase Temp (9 files)
`supabase/.temp/` directory (9 auto-generated files)

### Group 13 — Lock Files (2 files)
| File | Reason |
|------|--------|
| `src/frontend/package-lock.json` | Stale; pnpm used instead |
| `pnpm-lock.yaml` | Stale; regenerated by pnpm install |

---

## Deleted Beyond Original List (1 file — side-effect cleanup)

| File | Reason |
|------|--------|
| `src/frontend/src/shared/hooks/useMasteryAnalytics.ts` | Only imported by already-deleted `useMasteryPathOptimized.ts`; imported deleted `MasteryAnalyticsService` |

---

## Files Restored / Kept (3 files — still in use)

| File | Reason |
|------|--------|
| `src/frontend/src/entities/KnowledgeNode.ts` | Restored. Still imported by `useConcepts.ts` and `usePrefetchMastery.ts` |
| `src/frontend/src/entities/UserPath.ts` | Restored. Still imported by `useUserMastery.ts` and `usePrefetchMastery.ts` |
| `src/frontend/src/entities/Assessment/index.ts` | Restored. Still imported by `generateAssessment.ts`, `validateAssessment.ts`, `questionTemplates.ts`, `types.ts` |

---

## Verification Results

| Check | Status |
|-------|--------|
| `pnpm type-check` (tsc --noEmit) | ✅ Passed (0 errors) |
| `pnpm lint` (next lint) | ✅ Passed (0 warnings/errors) |
| `pnpm build` (next build) | ✅ Passed (22 routes, 234kB shared JS) |
| Backend server start | ✅ Started successfully |

---

## Summary

**Total files deleted:** 83 (across all groups)  
**Files kept despite plan:** 3 entities (still in use by live code)  
**Additional files deleted:** 1 hook (useMasteryAnalytics.ts — dead dependency chain)
