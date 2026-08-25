# Architecture — DEPRECATED (absorbed into SS-EDS docs/06-architecture/)

## System Design

```
┌──────────────────────────────────────────────────────────┐
│                    Browser (RTL/Arabic UI)                 │
└──────────────────┬───────────────┬───────────────────────┘
                   │               │
          ┌────────┴────┐   ┌──────┴────────┐
          │  Next.js    │   │  Axios Client  │
          │  API Routes │   │ (api.ts auto-  │
          │ (stubbed/   │   │  injects Bearer│
          │  TODO)      │   │  token)        │
          └──────┬──────┘   └──────┬─────────┘
                 │                 │
          ┌──────┴─────────────────┴──────────┐
          │        FastAPI Backend :8000        │
          │  ┌─────────────────────────────┐   │
          │  │   Routers (7 routers)       │   │
          │  │  ┌──────┬──────┬────────┐  │   │
          │  │  │Auth  │Paths │Assessm.│  │   │
          │  │  ├──────┼──────┼────────┤  │   │
          │  │  │Wizard│Progr.│Analyt. │  │   │
          │  │  ├──────┴──────┴────────┤  │   │
          │  │  │      Admin           │  │   │
          │  │  └─────────────────────┘  │   │
          │  └─────────────────────────────┘   │
          │              │                      │
          │  ┌───────────┴───────────┐          │
          │  │   SQLAlchemy ORM      │          │
          │  │   10 tables           │          │
          │  └───────────┬───────────┘          │
          └──────────────┼──────────────────────┘
                         │
            ┌────────────┴────────────┐
            │  SQLite (dev)           │
            │  PostgreSQL (prod)      │
            └─────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                    Services Layer                              │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │HybridLLM     │ │VectorSearch  │ │ProjectSubmission   │   │
│  │Provider      │ │Service       │ │Service             │   │
│  └──────┬───────┘ └──────┬───────┘ └────────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │Notification  │ │Conflict      │ │Gamification        │   │
│  │Service       │ │Checker       │ │(Python backend)    │   │
│  └──────────────┘ └──────────────┘ └────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

## Dual-Backend Pattern

| Aspect | FastAPI (Primary) | Next.js API Routes (Secondary) |
|--------|-------------------|-------------------------------|
| **Role** | Core business logic, data CRUD, auth, ~~gamification~~ | LLM proxy, search |
| **State** | Fully functional | Mostly stubbed with mock data + TODO comments |
| **Database** | SQLAlchemy (10 tables) | Intended for Supabase but not wired |
| **Auth** | JWT Bearer token (fully functional) | Custom `x-user-id` header (partially implemented) |

## Data Flow: Path Generation

```
User → Wizard (4 steps) → POST /api/generate-path/
  → run_assessment(goal, answers)       [assessor.py]
    → loads assessments.json
    → scores answers per skill
    → returns skill_levels dict (0-5 per skill)
  → updates Profile.skill_profile
  → generate_path(profile, goal, hours, prefs)  [generator.py]
    → fetch_skills_for_job_role()        [db_connector.py]
    → fetch_prerequisites_for_skills()   [db_connector.py]
    → topological_sort (Kahn's algorithm)
    → select_resources()                 [resources.json via DB]
    → returns structured path with steps
  → creates Path + PathStep records in DB
  → deduplicates resources by URL
  → returns full path to frontend
```

## Phase Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **2** | Core learning paths, wizard, assessments | Functional (SQLite backend) |
| **3** | Adaptive learning, mastery tracking | Partially implemented (AEIS schema) |
| **4.0** | Ecosystem synchrony, project submissions | Services exist, not wired |
| **4.5** | Vector search, embeddings | VectorSearchService exists, not integrated |

## Key Architectural Decisions

1. **Prerequisite DAG**: Learning paths use hardcoded prerequisite fallback + DB-sourced prereqs, sorted via Kahn's algorithm.
2. **SSE Real-time**: Step completions fire server-sent events; frontend invalidates React Query cache on receipt.
3. **Hybrid LLM**: Local-first (Ollama/mistral) → OpenAI fallback → static fallback. Never throws.
4. ~~**Gamification as side-effects**: XP/streaks/achievements fire during step completion, not as standalone events.~~ **REMOVED**
5. **Dual data sources**: Static JSON files (`rules.json`, `resources.json`, `assessments.json`) feed the generator, while `seed_all.py` populates the DB with overlapping data.
6. **Auth isolation**: FastAPI manages its own JWT auth (bcrypt + jose). Supabase auth is not used despite having the client configured.
