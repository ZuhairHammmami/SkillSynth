# Refactoring Guide

## Current Debt Register

### Pending Refactors
| Area | Issue | Priority | Status |
|------|-------|----------|--------|
| Backend DTO | Pydantic V2 migration (class Config → ConfigDict) | Medium | ✅ COMPLETE |
| Backend main.py | Deprecated `on_event` → lifespan | Medium | ✅ COMPLETE |
| Alembic | Replace `Base.metadata.create_all` with migrations | Medium | ✅ Initialized |
| Empty Layers | cache/, mappers/, exceptions/, metrics/, telemetry/, scheduler/, domain/, infrastructure/ | Low | ⬜ Pending |

### Completed Refactors
| Area | Change | Date |
|------|--------|------|
| Seed Script | Merged all seeds into `seed_v2.py` | June 2026 |
| Gamification | Removed XP, achievements from codebase | June 2026 |
| Profile Entity | Removed `total_xp`, `level` fields | June 2026 |
| Router Logic | Extracted all inline business logic to services | June 2026 |

## Refactoring Rules
1. Every refactor must have tests that pass before and after
2. No refactor > 300 lines change per commit
3. Always branch, never refactor on main
4. Add deprecation warnings before removing old API
5. Update docs in same PR as code change

## Migration Patterns
- **Router extraction**: Move inline logic to service class, test, then remove original
- **DTO migration**: Update schema, add `model_rebuild()` for circular refs, test
- **DB changes**: Create Alembic migration, update seed script, test both directions
