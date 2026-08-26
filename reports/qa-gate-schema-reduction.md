# SkillSynth — Schema-Reduction Final QA Gate (15-Table Core)

**Date**: 2026-08-25 · **Branch**: feature/smart-mentor-v1 · **Commits**: 14 (c6d0ff69..a68e07ac)

## Results

| # | Gate | Command | Result |
|---|------|---------|--------|
| 1 | Seed (idempotent ×2) | `PYTHONPATH=src python seed_v3.py` | ✅ 1109 rows, FK gate OK, both runs |
| 2 | Schema canonical | `PYTHONPATH=src python tools/verify_schema.py` | ✅ SCHEMA MATCH (15 tables, columns, PKs, FKs+ON DELETE, uniques, indexes) |
| 3 | Backend tests ×2 | `PYTHONPATH=src python -m pytest tests/ -q` | ✅ 80/80 passed both runs, isolated temp DB |
| 4 | Dev DB isolation | `sqlite3 skillsynth.db "SELECT count(*) FROM users;"` | ✅ 5 (untouched); FK check empty |
| 5 | Boot | `python -c "from backend.main import app"` | ✅ 46 paths / 56 ops |
| 6 | Live smoke | boot + curl | ✅ root, cached stats, flat /auth/me (7 keys), wizard-options, generate-path (200, steps), step complete, progress dashboard, analytics (mastered_skills/learning_velocity), admin aggregated 403-gate, events feed, SSE text/event-stream |
| 7 | Wizard assessment | GET /api/assessments/role/{title} + no-answer regeneration | ✅ 47 questions for Frontend Dev; no-downgrade proven by regression test |
| 8 | Student frontend | type-check + lint + build | ✅ 0 errors, 0 warnings |
| 9 | Admin app | type-check + build | ✅ 17 static routes |
| 10 | i18n parity | leaf-key diff | ✅ 583 = 583 identical sets |

## Final review disposition
Whole-branch review found 1 Critical + 3 Important + 5 Minor; all fixed except 2 parked with rulings (thin-router repo calls intentional; admin-SSE channel kept).

## Deliverables
- **Schema**: 29 → 15 tables (strict 3NF, 4 documented JSON exceptions), canonical DDL `src/migrations/003_reduced_schema.sql`, verifier hardened (ON DELETE + uniques).
- **Backend**: 8 layers, 7 routers (56 ops/46 paths), every table covered by ≥1 endpoint (ADR-013 matrix), Alembic removed.
- **Seed**: seed_v3.py — all 15 tables, ~1109 rows, FK-gated, idempotent.
- **Tests**: 80 tests (auth/catalog/learning/assessments/analytics/admin/realtime/schema + wizard-scoring regression), isolated DB.
- **Frontend**: real wizard assessment quiz (collects answers → generate-path), no-downgrade proficiency, landing stats via env URL, dev reset link, dead hooks/types/keys pruned (i18n 824→583, parity kept).
- **Admin**: RBAC roles UI removed, settings card dropped, Role types cleaned.
- **Docs**: ADR-013 (rationale + table→API matrix), AGENTS.md/README/INDEX/ERD regenerated from ORM.