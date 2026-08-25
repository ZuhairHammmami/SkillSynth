# Decision Log

## ADR-001: Clean Architecture (20 Layers)
**Date**: 2026-06-01  
**Context**: Need a maintainable backend structure that enforces separation of concerns.  
**Decision**: Adopt 20-layer Clean Architecture with strict dependency flow: Router → Service → Repository → Entity. No business logic in routers, no SQL in services.  
**Consequences**: +Maintainability, +Testability, -More files to navigate. Enforced via code review.

## ADR-002: No Gamification
**Date**: 2026-06-01  
**Context**: Original design included XP, levels, streaks, achievements.  
**Decision**: Remove ALL gamification mechanics. Users are motivated by career progress, not points. Streaks retained as a lightweight engagement metric (not displayed in UI).  
**Consequences**: -Removed xp_transactions, achievements tables. Cleaner UX. More honest analytics.

## ADR-003: Admin/Student Separation
**Date**: 2026-06-01  
**Context**: Risk of feature bleed between admin and student interfaces.  
**Decision**: Two completely separate route groups in Next.js: `/admin` and `/(student)`. Different layouts, different nav, different data queries. Shared only UI primitives.  
**Consequences**: +Clear separation, -Some code duplication in admin CRUD pages.

## ADR-004: Deterministic Path Generation
**Date**: 2026-06-01  
**Context**: Should path generation use LLMs or deterministic algorithms?  
**Decision**: Kahn's topological sort on prerequisite DAG. Deterministic only. Same inputs → same outputs. LLM used only for optional resource enrichment.  
**Consequences**: +Predictable, +Testable, +No LLM cost, -Less "creative" paths.

## ADR-005: SQLite Dev / PostgreSQL Prod
**Date**: 2026-06-01  
**Context**: Need different DB setups for development and production.  
**Decision**: SQLite for local dev (zero config), PostgreSQL for production (Supabase). Mode switch via `MODE` env var. SQLAlchemy ORM abstracts differences.  
**Consequences**: +Fast development iteration, -Some SQLite-specific pragmas needed.

## ADR-006: Pydantic V2 Migration
**Date**: 2026-06-25  
**Context**: Pydantic V2 has been stable; V1 deprecated.  
**Decision**: Migrate all DTOs from `class Config` to `model_config = ConfigDict`. Replace `update_forward_refs` with `model_rebuild`. Replace `Field(example=...)` with `Field(json_schema_extra={"example": ...})`.  
**Consequences**: +Future-proof, -10 DTO files needed individual edits.

## ADR-007: Alembic Migration Adoption
**Date**: 2026-06-25  
**Context**: SQLAlchemy `Base.metadata.create_all()` is not suitable for production.  
**Decision**: Initialize Alembic, stamp current schema, create migration for future changes.  
**Consequences**: +Production-ready migrations, -Need to maintain migration scripts alongside model changes.
