# SS-EDS: Diagrams

## Purpose
Document diagram resources for SkillSynth: entity-relationship diagram (36 tables), Clean Architecture layer flow, request lifecycle, data flow, component hierarchy, and route structure.

## Responsibilities
- Maintain up-to-date ERD diagram matching 36-table schema
- Document Clean Architecture layer interaction flows
- Provide request lifecycle diagrams for key operations
- Maintain data flow diagrams for learning engine and realtime
- Ensure diagrams match current implementation

## Inputs
- Database schema changes (003_reduced_schema.sql)
- Architectural decisions (Clean Architecture layers)
- Use case updates (frontend routes, API endpoints)

## Outputs
- ERD diagram (docs/40-diagrams/ERD.md)
- Architecture flow diagrams (inline in docs)
- Request lifecycle diagrams (inline in docs)
- Data flow diagrams for learning engine and realtime

## Dependencies
- 10-database (schema for ERD)
- 06-architecture (Clean Architecture layer definitions)
- 07-backend (routers, services, repositories layer structure)

## Diagram Inventory
| Diagram | Location | Format | Last Updated |
|---------|----------|--------|--------------|
| ERD (36 tables) | docs/40-diagrams/ERD.md | Mermaid | Current |
| Clean Architecture Flow | docs/40-diagrams/INDEX.md | ASCII | Current |
| Request Lifecycle | docs/40-diagrams/INDEX.md | ASCII | Current |
| Learning Engine Data Flow | docs/11-learning-engine/INDEX.md | ASCII | Current |
| SSE Connection Lifecycle | docs/12-realtime/INDEX.md | ASCII | Current |
| Auth Flow | docs/35-auth/INDEX.md | ASCII | Current |

## Sequence: Clean Architecture Request Lifecycle
```
Client → HTTP Request
  → Router (thin handler, no business logic)
    → Policy (auth check dependency)
      → Service (business logic, no SQL)
        → Query/Repository (SQLAlchemy data access)
          → Entity (SQLAlchemy model)
            → Database
          ← ORM result
        ← Business object
      ← Processed result
    ← Auth context
  ← Response DTO
Client ← JSON Response
```

## Sequence: Data Flow — Frontend to Database
```
React Component → React Query Hook → API Client (fetch)
  → Next.js API Route / FastAPI Backend
    → Router → Policy → Service → Repository → DB
  ← JSON Response
← React Query Cache → Component Re-render
```

## Component Hierarchy (Frontend)
```
Layout (RTL: ar, LTR: en)
  ├── AdminLayout (separate nav, dashboard)
  │   ├── AdminDashboard
  │   ├── AdminUsers
  │   ├── AdminPaths
  │   ├── AdminAnalytics
  │   └── AdminSettings
  └── AppLayout
      ├── AuthGuard
      ├── PathsList → PathDetail → StepView
      ├── Skills → KnowledgeGraph → SkillDetail
      ├── Analytics → Dashboard → Reports
      ├── Resources → ResourceList
      └── Profile → Settings
```

## Route Structure
| Prefix | Routes | Description |
|--------|--------|-------------|
| /api/auth/* | 10 routes | Login, register, me, refresh, sse-token |
| /api/paths/* | 8 routes | CRUD paths, steps, completion |
| /api/learning/* | 7 routes | Graph, path gen, analysis, recommendations |
| /api/admin/* | 9 routes | Users, paths, categories, reports |
| /api/analytics/* | 5 routes | Dashboard, progress, engagement |
| /api/realtime/* | 3 routes | SSE events, notify, broadcast |
| /ws | 1 route | WebSocket endpoint |

## Rules
1. Diagrams must be in Mermaid format (GitHub-rendered) or ASCII for inline docs
2. All diagrams must be version controlled
3. Diagrams must be updated when schema/architecture changes
4. Complex diagrams should have simplified reference versions
5. ERD must include FK annotations and index markers

## Examples
- ERD Mermaid: `erDiagram users ||--o| profiles : "has"`
- Architecture: ASCII art with box-drawing characters

## Edge Cases
- Mermaid rendering differences between editors → test in GitHub
- Large ERD (36 tables) needs focused sub-diagrams for readability
- Diagram outdated after schema migration → flagged in PR review

## Failure Cases
- Diagram not updated after schema → misleading documentation
- Mermaid syntax error → diagram not rendered in Markdown
- Architecture diagram too complex → unreadable, needs simplification

## Recovery Procedures
1. Validate Mermaid syntax with online validator
2. Review diagram against current implementation
3. Update and commit corrected diagram

## Refactoring Strategy
- Automate ERD generation from SQLAlchemy entity models
- Add CI check for diagram staleness
- Create focused sub-diagrams for each table family
