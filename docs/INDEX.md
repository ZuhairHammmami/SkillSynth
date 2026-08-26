# SkillSynth SS-EDS Documentation

> **SS-EDS**: SkillSynth Engineering Documentation System

## Overview
Complete documentation for SkillSynth, an adaptive learning platform: **FastAPI + SQLAlchemy** backend (Clean Architecture, 8 routers), **two Next.js 14 apps** (student ar/en RTL-first :3000, admin English-only :3001) on **pnpm**, and a **strict-3NF 15-table database** (SQLite dev / PostgreSQL prod).

## Documentation Structure

### Foundation
| # | Section | Description |
|---|---------|-------------|
| 00 | [Principles](00-principles/INDEX.md) | Design axioms, flat visual mandate, docs-truth rules |
| 01 | [Product](01-product/INDEX.md) | Value proposition, personas, feature catalog |
| 02 | [Business](02-business/INDEX.md) | Business model, cost posture |
| 03 | [Functional Requirements](03-functional-requirements/INDEX.md) | Feature requirements, acceptance criteria |
| 04 | [Non-Functional Requirements](04-non-functional-requirements/INDEX.md) | Performance budgets, quality gates |
| 05 | [Domain](05-domain/INDEX.md) | Ubiquitous language, domain rules |

### Architecture & Implementation
| # | Section | Description |
|---|---------|-------------|
| 06 | [Architecture](06-architecture/INDEX.md) | Clean Architecture layers, request lifecycle |
| 07 | [Backend](07-backend/INDEX.md) | Routers/services/repositories/entities/dto layout |
| 08 | [Frontend](08-frontend/INDEX.md) | Student app structure (app/shared/i18n/types), i18n, state |
| 09 | [Admin](09-admin/INDEX.md) | Admin app (:3001), CRUD pages + force-delete flow, binary admin gate |
| 10 | [Database](10-database/INDEX.md) | 15 tables, canonical DDL, seed_v3, verifier |
| 11 | [Learning Engine](11-learning-engine/INDEX.md) | Path generation, prerequisite DAG, scoring |
| 12 | [Realtime](12-realtime/INDEX.md) | SSE streams and event payloads |
| 13 | [Localization](13-localization/INDEX.md) | Bilingual ar/en, RTL-first strategy |
| 14 | [Security](14-security/INDEX.md) | JWT 24h, lockout, CSRF/CSP/HSTS, rate limits |
| 15 | [Performance](15-performance/INDEX.md) | Inline TTL cache, compression, batched queries |
| 16 | [Testing](16-testing/INDEX.md) | pytest suite reality and isolation model |
| 17 | [Deployment](17-deployment/INDEX.md) | run.py/uvicorn, Docker files, env vars |
| 18 | [Monitoring](18-monitoring/INDEX.md) | activity_log audit trail, health endpoint |

### Conventions & Design
| # | Section | Description |
|---|---------|-------------|
| 19 | [Conventions](19-conventions/INDEX.md) | Coding standards, imports, commits |
| 20 | [UI System](20-ui-system/INDEX.md) | Design tokens, Linear/Notion-style system |
| 21 | [Accessibility](21-accessibility/INDEX.md) | WCAG AA, keyboard nav, contrast matrix |

### API & Events
| # | Section | Description |
|---|---------|-------------|
| 22 | [API](22-api/INDEX.md) | Endpoint reference — 68 operations across 54 paths (8 routers) |
| 23 | [Events](23-events/INDEX.md) | SSE event catalog |
| 24 | [Caching](24-caching/INDEX.md) | 30s TTL inline cache on /api/public/stats |
| 25 | [CLI](25-cli/INDEX.md) | seed_v3.py + tools/verify_schema.py commands |

### Platform Sections
| # | Section | Description |
|---|---------|-------------|
| 26 | [Resource Engine](26-resource-engine/INDEX.md) | resources table, step resource selection |
| 27 | [Analytics](27-analytics/INDEX.md) | Dashboard keys, skill growth, velocity |
| 28 | *(removed)* | Numbered slot retired with its feature (ADR-013) — number never reused |
| 29 | [Roadmaps](29-roadmaps/INDEX.md) | Current-state snapshot, active queue |
| 30 | [Images](30-images/INDEX.md) | Favicons, avatar fallbacks |
| 31 | [File Storage](31-file-storage/INDEX.md) | Storage posture (no uploads today) |
| 32 | [User Profile](32-user-profile/INDEX.md) | users table, user_skills proficiency |
| 33 | [Admin Profile](33-admin-profile/INDEX.md) | Binary is_admin authorization |
| 34 | [Error Handling](34-error-handling/INDEX.md) | Handlers in main.py, integrity semantics, boundaries |
| 35 | [State Management](35-state-management/INDEX.md) | Frontend data/cache patterns |

### Quality & Governance
| # | Section | Description |
|---|---------|-------------|
| 36 | [Component Library](36-component-library/INDEX.md) | Component inventory |
| 37 | [Clean Code](37-clean-code/INDEX.md) | Principles, single-purpose functions |
| 38 | [Refactoring](38-refactoring/INDEX.md) | Debt management patterns |
| 39 | [Future](39-future/INDEX.md) | Candidates with ADR entry gates |
| 40 | [Diagrams](40-diagrams/INDEX.md) | ERD + lifecycle sequences |
| 41 | [Decision Records](41-decision-records/INDEX.md) | ADR index incl. supersessions; integrity policy in adr-014.md |
| 42 | [Runbooks](42-runbooks/INDEX.md) | Verified operational commands |
| 43 | [Checklists](43-checklists/INDEX.md) | Pre-commit, review gates |
| 44 | [Test Scenarios](44-test-scenarios/INDEX.md) | Suite map: 190 tests / 21 files |
| 45 | [Release Notes](45-release-notes/INDEX.md) | Changelog, newest first |
| 46 | [Glossary](46-glossary/INDEX.md) | Current terminology only |
| 47 | [Contributing](47-contributing/INDEX.md) | PR process |
| 48 | [Style Guide](48-style-guide/INDEX.md) | TS/React/Python/CSS rules |
| 49 | [Module Boundaries](49-module-boundaries/INDEX.md) | Import direction rules |
| 50 | [Anti-Patterns](50-anti-patterns/INDEX.md) | Banned practices + guards |
| 51 | [AI Integration](51-ai-integration/INDEX.md) | Local LLM endpoints, bounded autonomy, degradation ladder (ADR-015) |

## Quick Start
```bash
# Backend (:8000)
source .venv/bin/activate && pip install -r requirements.txt && PYTHONPATH=src python run.py

# Student frontend (:3000)
cd src/frontend && pnpm dev

# Admin app (:3001)
cd src/admin-app && pnpm dev
```

## Quick Reference
- **Seed**: `PYTHONPATH=src python seed_v3.py` (~1109 rows, FK-gated, idempotent)
- **Tests**: `PYTHONPATH=src python -m pytest tests/ -q` — 190 passed, isolated temp DB per run
- **Schema**: `PYTHONPATH=src python tools/verify_schema.py` → SCHEMA MATCH (15 tables)
- **API**: 8 routers · 54 paths · 68 operations; OpenAPI UI at `http://localhost:8000/docs`
- **Integrity**: restricted deletes → 409 census + `?force=true`; cycles and bad refs rejected at write time ([ADR-014](41-decision-records/adr-014.md))
- **Status**: August 2026 — integrity layer shipped (ADR-014 accepted)

## File Stats
- **Sections**: 51 numbered slots (28 retired after feature removal); every live section has an INDEX.md
- **Last updated**: August 2026
