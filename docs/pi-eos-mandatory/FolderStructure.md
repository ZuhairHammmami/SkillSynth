# Folder Structure

```
/media/zuhair/Extra/SkillSynth/
├── docs/                               # SS-EDS Documentation (51 dirs)
│   ├── pi-eos-mandatory/               # PI-EOS v2.0 mandatory docs (27 files)
│   ├── 00-principles/ ... 50-anti-patterns/
│   ├── INDEX.md                        # Master table of contents
│   └── *.md (ARCHITECTURE, API, AUTH, BACKEND, etc.)
├── src/
│   ├── backend/                        # FastAPI Clean Architecture
│   │   ├── main.py                     # App entry, middleware, router mounts
│   │   ├── database.py                 # SQLAlchemy engine + session
│   │   ├── limiter.py                  # Rate limiting (slowapi)
│   │   ├── routers/                    # 9 routers (~85 endpoints)
│   │   │   └── learning/              # Sub-routers (analysis, generation, progress, recommendations)
│   │   ├── services/                   # 13 business logic services
│   │   ├── repositories/              # 9 data access repositories
│   │   ├── entities/                   # SQLAlchemy models (one per file)
│   │   ├── dto/                        # Pydantic V2 schemas (10 files)
│   │   ├── validators/                # Input validators
│   │   ├── policies/                   # Auth guards (get_current_user, get_current_admin_user)
│   │   ├── middlewares/               # CORS, Security, CSRF, Compression
│   │   ├── events/                     # SSE publisher
│   │   ├── commands/                   # CQRS command handlers
│   │   ├── queries/                    # CQRS query handlers
│   │   ├── cache/                      # Caching decorators (empty)
│   │   ├── config/                     # App settings
│   │   ├── mappers/                    # Entity<->DTO mapping (empty)
│   │   ├── infrastructure/            # Infrastructure (empty)
│   │   ├── scheduler/                 # Background tasks (empty)
│   │   ├── metrics/                   # Prometheus (empty)
│   │   └── telemetry/                 # OpenTelemetry (empty)
│   ├── frontend/                       # Next.js 14 App Router
│   │   └── src/
│   │       ├── app/                   # Page files (24 routes)
│   │       │   ├── (auth)/            # Login, Register, Forgot/Reset Password
│   │       │   ├── (student)/         # Dashboard, Learn, Profile, Analytics, Settings
│   │       │   └── admin/             # 11 admin pages
│   │       ├── shared/                # Reusable components, hooks, UI
│   │       ├── i18n/                  # next-intl config + messages (en/ar)
│   │       └── types/                 # TypeScript type definitions
│   ├── data/                           # Learning engine data
│   │   └── learning_paths/            # generator.py, assessor.py, rules.json, etc.
│   └── migrations_alembic/            # Alembic migrations
├── tests/                              # Backend pytest suite (67 tests)
├── seed_v2.py                          # Authoritative seed script
├── run.py                              # Backend startup
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Pytest config
├── .env                                # Backend environment variables
├── alembic.ini                         # Alembic configuration
└── reports/archive/                      # Superseded audit-era artifacts (incl. compact-report.md)
```
