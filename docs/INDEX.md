# SkillSynth SS-EDS Documentation

> **SS-EDS**: SkillSynth Engineering Documentation System

## Overview
Complete documentation for the SkillSynth Adaptive Learning OS — a modular synthesizer-inspired platform with dual-backend architecture (FastAPI + Next.js), RTL/Arabic-first design, gamified learning paths, and LLM augmentation.

## Documentation Structure

### Foundation
| # | Section | Description | Source |
|---|---------|-------------|--------|
| 00 | [Principles](00-principles/INDEX.md) | Design axioms, RTL-first philosophy, flat color mandate | |
| 01 | [Product](01-product/INDEX.md) | Value proposition, personas, feature catalog, roadmap | |
| 02 | [Business](02-business/INDEX.md) | Business model, monetization, cost management | |
| 03 | [Functional Requirements](03-functional-requirements/INDEX.md) | Feature requirements, acceptance criteria, traceability | |
| 04 | [Non-Functional Requirements](04-non-functional-requirements/INDEX.md) | Performance budgets, SLAs, quality gates | |
| 05 | [Domain](05-domain/INDEX.md) | Ubiquitous language, bounded contexts, domain rules | |

### Architecture & Implementation
| # | Section | Description | Source |
|---|---------|-------------|--------|
| 06 | [Architecture](06-architecture/INDEX.md) | System design, dual-backend, data flow, ADRs | `ARCHITECTURE.md` |
| 07 | [Backend](07-backend/INDEX.md) | FastAPI structure, routers, models, startup | `BACKEND.md` |
| 08 | [Frontend](08-frontend/INDEX.md) | Next.js structure, routing, state, i18n | `FRONTEND.md` |
| 09 | [Admin](09-admin/INDEX.md) | Admin Central Laboratory, Patch Builder, Wave Shaper | `ADMIN_LAB_SPEC.md` |
| 10 | [Database](10-database/INDEX.md) | Schema (15 tables, canonical DDL), seed, indexes | `BACKEND.md`, `DATA.md` |
| 11 | [Learning Engine](11-learning-engine/INDEX.md) | Path generation, DAG resolver, assessment scoring | |
| 12 | [Realtime](12-realtime/INDEX.md) | SSE events, connection lifecycle, audit logging | `BACKEND.md`, `API.md` |
| 13 | [Localization](13-localization/INDEX.md) | i18n strategy, next-intl, RTL-first approach | |
| 14 | [Security](14-security/INDEX.md) | JWT auth, RBAC (6 roles), rate limiting, headers | `AUTH.md` |
| 15 | [Performance](15-performance/INDEX.md) | Benchmarks, optimization, N+1 prevention | |
| 16 | [Testing](16-testing/INDEX.md) | Verification commands, gaps, CI/CD status | `TESTING.md` |
| 17 | [Deployment](17-deployment/INDEX.md) | Build, deploy, env vars, Render/Vercel/Supabase | `DEPLOYMENT.md` |
| 18 | [Monitoring](18-monitoring/INDEX.md) | Observability, audit, alerting, health reports | |

### Conventions & Design
| # | Section | Description | Source |
|---|---------|-------------|--------|
| 19 | [Conventions](19-conventions/INDEX.md) | Coding standards, imports, commits | `AGENTS.md` |
| 20 | [UI System](20-ui-system/INDEX.md) | Design tokens, layout, navigation, 29 components | `DESIGN_SYSTEM.md`, `LAYOUT_NAVIGATION.md` |
| 21 | [Accessibility](21-accessibility/INDEX.md) | WCAG AA, ARIA, keyboard nav, touch targets | |

### API & Events
| # | Section | Description | Source |
|---|---------|-------------|--------|
| 22 | [API](22-api/INDEX.md) | Endpoint reference (55 operations across 45 paths) | `API.md` |
| 23 | [Events](23-events/INDEX.md) | Event catalog, SSE, audit, UI event bus | |
| 24 | [Caching](24-caching/INDEX.md) | React Query, cache invalidation, stale-while-revalidate | |

### Infrastructure & Services
| # | Section | Description |
|---|---------|-------------|
| 25 | [CLI](25-cli/INDEX.md) | ~~Command reference, seed scripts, verification~~ **DEPRECATED — removed** |
| 26 | [Resource Engine](26-resource-engine/INDEX.md) | Resource selection, filtering, deduplication |
| 27 | [Analytics](27-analytics/INDEX.md) | Learner analytics, admin reports, skill growth |
| 28 | [Gamification](28-gamification/INDEX.md) | ~~XP, levels, streaks, achievements~~ **DEPRECATED — feature removed** |
| 29 | [Roadmaps](29-roadmaps/INDEX.md) | Phase tracker, completed work, future plans |
| 30 | [Images](30-images/INDEX.md) | SVG icons, avatars, optimization |
| 31 | [File Storage](31-file-storage/INDEX.md) | Uploads, storage backends, security |
| 32 | [User Profile](32-user-profile/INDEX.md) | Profile model, skill profile, preferences |
| 33 | [Admin Profile](33-admin-profile/INDEX.md) | Admin users, roles, permissions |
| 34 | [Error Handling](34-error-handling/INDEX.md) | Exception handlers, ErrorBoundary, fallbacks |
| 35 | [State Management](35-state-management/INDEX.md) | React Query, Zustand, useState, Sonner |

### Quality & Architecture
| # | Section | Description |
|---|---------|-------------|
| 36 | [Component Library](36-component-library/INDEX.md) | shadcn/ui + 29 custom synth components |
| 37 | [Clean Code](37-clean-code/INDEX.md) | Principles, DRY, single responsibility |
| 38 | [Refactoring](38-refactoring/INDEX.md) | Debt management, migration patterns |
| 39 | [Future](39-future/INDEX.md) | Long-term vision, planned features |
| 40 | [Diagrams](40-diagrams/INDEX.md) | ERD, UML, architecture diagrams |
| 41 | [Decision Records](41-decision-records/INDEX.md) | ADRs + stale root file archives (cleanup artifacts) |
| 42 | [Runbooks](42-runbooks/INDEX.md) | Operational procedures, incident response |
| 43 | [Checklists](43-checklists/INDEX.md) | Pre-commit, PR review, release checklists |
| 44 | [Test Scenarios](44-test-scenarios/INDEX.md) | Manual test cases, Gherkin scenarios |
| 45 | [Release Notes](45-release-notes/INDEX.md) | Phase release history, migration guides |
| 46 | [Glossary](46-glossary/INDEX.md) | Terminology, metaphor replacements |
| 47 | [Contributing](47-contributing/INDEX.md) | PR process, coding standards |
| 48 | [Style Guide](48-style-guide/INDEX.md) | TS/React/Python/CSS formatting rules |
| 49 | [Module Boundaries](49-module-boundaries/INDEX.md) | Dependency direction, import rules |
| 50 | [Anti-Patterns](50-anti-patterns/INDEX.md) | What NOT to do, with examples and fixes |

## Existing Files Mapped to New Structure
| Old File | New Location |
|----------|--------------|
| ARCHITECTURE.md | `06-architecture/INDEX.md` |
| BACKEND.md | `07-backend/INDEX.md`, `10-database/INDEX.md` |
| FRONTEND.md | `08-frontend/INDEX.md` |
| API.md | `22-api/INDEX.md`, `12-realtime/INDEX.md` |
| AUTH.md | `14-security/INDEX.md` |
| DATA.md | `10-database/INDEX.md`, `11-learning-engine/INDEX.md` |
| SERVICES.md | `12-realtime/INDEX.md` |
| TESTING.md | `16-testing/INDEX.md` |
| DEPLOYMENT.md | `17-deployment/INDEX.md` |
| DESIGN_SYSTEM.md | `20-ui-system/INDEX.md`, `36-component-library/INDEX.md` |
| LAYOUT_NAVIGATION.md | `20-ui-system/INDEX.md` |
| LEARNER_EXPERIENCE.md | `20-ui-system/INDEX.md`, `11-learning-engine/INDEX.md` |
| MANAGER_STUDIO.md | `09-admin/INDEX.md` |
| MICRO_UX_PHYSICS.md | `20-ui-system/INDEX.md` |
| RESPONSIVE_DESIGN.md | `20-ui-system/INDEX.md` |
| ADMIN_LAB_SPEC.md | `09-admin/INDEX.md` |
| AGENTS.md | `19-conventions/INDEX.md` |

## Quick Reference
- **Build**: `cd src/frontend && pnpm dev` (Frontend :3000), `cd src/admin-app && pnpm dev` (Admin :3001), `python run.py` (Backend :8000)
- **Seed**: `PYTHONPATH=src python seed_v3.py`
- **Verify**: `cd src/frontend && pnpm type-check && pnpm lint && pnpm build`; `cd src/admin-app && pnpm type-check && pnpm build`; `PYTHONPATH=src python -m pytest tests/ -q`; `python tools/verify_schema.py`
- **Status**: 79/79 tests passing (isolated temp SQLite DB), frontend and admin builds green, backend serves 55 operations across 45 paths, admin CRUD complete

## File Stats
- **Total directories**: 51
- **Total INDEX.md files**: 51
- **Existing docs absorbed**: 16 flat files
- **Last updated**: August 2026
