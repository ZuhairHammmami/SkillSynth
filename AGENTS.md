**SkillSynth — Agent Guide (15-Table Core)**  
*Adaptive Learning OS — SS-EDS documented, Clean Architecture, 15-table strict-3NF database.*

**Quick Start**  
```
# Backend (port 8000)
source .venv/bin/activate && pip install -r requirements.txt && PYTHONPATH=src python run.py

# Frontend (port 3000)
export PATH="$PATH:/home/zuhair/.npm-global/bin"   # if pnpm is not on PATH
cd src/frontend && pnpm dev

# Admin app (port 3001)
cd src/admin-app && pnpm dev

# Seed database
PYTHONPATH=src python seed_v3.py    # 15-table seed (~1109 rows, FK-gated, idempotent)

# Tests
PYTHONPATH=src python -m pytest tests/ -q    # 142 tests, isolated temp DB
```

**Verification**  
```
cd src/frontend && pnpm type-check   # tsc --noEmit
cd src/frontend && pnpm lint         # next lint (zero warnings)
cd src/frontend && pnpm build        # type-check + next build
cd src/admin-app && pnpm type-check && pnpm build
PYTHONPATH=src python -m pytest tests/ -q
PYTHONPATH=src python tools/verify_schema.py   # prints SCHEMA MATCH on success
```

**Architecture Overview**  
| Layer | Tech | Location |
|-------|------|----------|
| **Backend** | FastAPI + SQLAlchemy (Clean Architecture) | `src/backend/` — 8 layers; 63 operations across 49 paths (7 routers) |
| **Frontend (student)** | Next.js 14 + React 18 + Tailwind + shadcn/ui | `src/frontend/` :3000 — src/{app,shared,i18n,types} + middleware.ts, bilingual ar/en |
| **Admin** | Separate Next.js app (English-only) | `src/admin-app/` :3001 — own layout, nav, state |
| **Database** | SQLite (dev) / PostgreSQL (prod) | `skillsynth.db` — 15 domain tables, strict 3NF (one documented JSON exception); canonical DDL at `src/migrations/003_reduced_schema.sql` |
| **Documentation** | SS-EDS | `docs/` — 49 live sections (50 numbered slots, 28 retired) + root index |

**Current System State**  
| Component | Status | Evidence |
|-----------|--------|----------|
| **SS-EDS Documentation** | ✅ 49 section dirs with INDEX.md | 00-principles through 50-anti-patterns; slot 28 retired with its feature |
| **Backend Clean Architecture** | ✅ All files <300 lines | 8 layers, 7 routers, 0 circular imports; commands/queries/cache/infrastructure/ removed with the features they served (ADR-013) |
| **Database 15-table 3NF** | ✅ Canonical DDL + verifier | `src/migrations/003_reduced_schema.sql`, `tools/verify_schema.py` → SCHEMA MATCH (compares tables/columns/PKs/FKs/ON DELETE/uniques) |
| **Frontend Redesign** | ✅ Linear/Notion style, no gradients/neon | Bilingual ar/en RTL-first, 560 i18n leaf keys parity, error boundaries (`app/error.tsx`, `global-error.tsx`) |
| **Admin Application** | ✅ Separate app at `src/admin-app` :3001 | Full CRUD dialogs (users/skills/resources/categories/job-roles) incl. PUTs and force-delete flow, change-password functional, Feature Flags page (read-only); roles UI removed |
| **Localization** | ✅ 100% bilingual AR/EN | 0 hardcoded strings, dynamic RTL/LTR |
| **Learning Engine** | ✅ Deterministic, topological sort | Prerequisites graph (skill_prerequisites), gap analysis, wizard scoring → user_skills |
| **Real-time** | ✅ SSE | `/api/realtime/events` + `/api/events` alias, token-auth streams |
| **Performance** | ✅ Cache, compression | 30s TTL inline cache on `/api/public/stats`; compression middleware |
| **Security** | ✅ OWASP Top 10 | Rate limiting, CSRF, CSP, HSTS, activity_log audit trail |
| **Referential Integrity** | ✅ Write-time guards (ADR-014) | FK validation→400 naming bad ref; rename-uniqueness (case-insensitive)→409; category/prerequisite cycle guards→400; restricted deletes skills/categories/job_roles→409 `{"detail":{"message","dependents"}}` unless `?force=true`; IntegrityError→409 safety net in main.py |
| **QA** | ✅ 142/142 tests passed ×2 | Isolated temp SQLite DB per run; dev DB never touched |

**Backend Layer Structure (`src/backend/`)**  
```
routers/       → 7 thin handlers + catalog_admin merged under /api/admin + shared error_mapping (auth · learning · paths · assessments · analytics · admin · realtime)
services/      → 8 business-logic modules (auth · catalog · catalog_integrity · wizard · learning · assess · analytics · admin)
repositories/  → 6 data-access modules (identity · catalog · learning · assess · engagement · integrity)
entities/      → 5 consolidated model modules (+base.py) — 15 tables
dto/           → 4 Pydantic schema modules (auth · catalog · learning · admin)
policies/      → get_current_user + require_admin (is_admin gate)
middlewares/   → Security headers, CSRF (prod-only), compression
events/        → In-memory SSE pub/sub (publisher.py)
```
Note: `mappers/`, `validators/`, `commands/`, `queries/`, `cache/`, `infrastructure/` layers were removed as dead code or dissolved with the features they served (see ADR-013). Migration tooling is removed — schema truth is DDL + ORM + seed.

**Critical Conventions**  
| Rule | Detail |
|------|--------|
| **Python imports** | `from backend import X` — `run.py` injects `src/` into PYTHONPATH |
| **Package manager** | **pnpm** for frontend and admin app (not npm) |
| **Frontend working dir** | Always `cd src/frontend` first (admin: `cd src/admin-app`) |
| **RTL-first** | `<html lang="ar" dir="rtl">` — Tajawal font |
| **Auth** | JWT Bearer token 24h (stateless; no sessions table), account lockout (5 attempts), binary `is_admin` role gate |
| **Design system** | No neon, gradients, glassmorphism. Linear/Notion/Stripe style |
| **Function style** | No function > 40 lines; **every function carries a docstring stating its single purpose and its caller/callee relationships** (user-mandated) |
| **File size limit** | No file > 300 lines (seed_v3.py is the documented exception — data module) |
| **Database** | 15 domain tables, strict 3NF; JSON columns limited to the 4 documented exceptions (assessment_questions.options, path_steps.resource_ids/assessment_ids, activity_log.data) |

**Seed Credentials**  
| User | Email | Password |
|------|-------|----------|
| Admin | admin@skillsynth.io | Admin@123456 |
| Demo | demo@demo.com | demo123 |
| Editor | editor@skillsynth.io | Editor@123456 |
| Veteran | veteran@skillsynth.io | Veteran@123456 |
| Student2 | student2@skillsynth.io | Student@123456 |

**API Surface (dev mode)**  
| Endpoint | Notes |
|----------|-------|
| *(total)* | 63 OpenAPI operations across 49 paths (7 routers): Admin 30 ops/19 paths · Paths & Progress 9/7 · Auth 8/7 · Analytics 4/4 · Assessments 3/3 · Learning Engine 3/3 · Real-time 2/2 · untagged utility ops 4 (`/`, `/api/events` alias, `/api/public/stats`, `/api/wizard-options`) |
| `/api/auth/*` | register, token, me (GET/PUT), change-password, forgot/reset (stateless signed token), sse-token, csrf |
| `/api/generate-path/` + `/api/learning/*` | Path generation (wizard scoring), graph, gaps; `/api/learning/generate` alias |
| `/api/paths/` + `/api/steps/*` | Path CRUD, step complete/undo, progress dashboard |
| `/api/assessments/*` | Questions per skill and per role (`/api/assessments/role/{job_role_title}`), submit → results + user_skills |
| `/api/analytics/*` | dashboard (incl. mastered_skills, learning_velocity), skill-growth, path-progress, learning-history |
| `/api/admin/*` | Users/skills/categories/resources/job-roles CRUD (GET/POST/PUT/DELETE; skills/categories/job-roles deletes restricted → 409 unless `?force=true`) + assessments list/delete + events feed + reports/aggregated + system-health + backups + db-inspector + feature flags |
| `/api/realtime/events` + `/api/events` | SSE streaming (token-auth) |
| `/api/public/stats` | Public stats, 30s TTL inline cache |
| `/api/wizard-options` | Job roles + preference literals for the wizard |

**Documentation**  
- SS-EDS at `docs/` — 51 directories with INDEX.md files  
- Root `docs/INDEX.md` — master table of contents  
- Backend docs: `docs/07-backend/`  
- Frontend docs: `docs/08-frontend/`  
- Database docs: `docs/10-database/` + `docs/40-diagrams/ERD.md`  
- Schema-reduction rationale + table→API matrix: `docs/41-decision-records/adr-013.md`
- Referential-integrity policy (restricted deletes, cycle guards): `docs/41-decision-records/adr-014.md`

**Agentic Workflow**  
Tasks with 3+ steps MUST be distributed across sub-agents. Scale: 3-5 steps → 4-6 agents, 6-10 steps → 7-10 agents, 11+ → 13+ agents. Each sub-agent gets exact files to edit, edit patterns, and verification commands. Primary agent coordinates, merges, and verifies.

**Environment Files**  
- `.env` — Backend config (DB, LLM, API keys). **Live credentials — needs rotation**.  
- `src/frontend/.env.local` — Frontend vars. **Live credentials — needs rotation**.