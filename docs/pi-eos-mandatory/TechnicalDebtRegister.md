# Technical Debt Register

## Active Debt Items

| ID | Area | Description | Impact | Effort | Priority |
|----|------|-------------|--------|--------|----------|
| TD-001 | Backend | 8 empty layers: cache/, mappers/, exceptions/, metrics/, telemetry/, scheduler/, domain/, infrastructure/ | Architecture drift risk, unused imports confusion | 2 days | Low |
| TD-002 | Database | No Alembic migration for existing schema (only stamped) | Cannot rollback schema changes | 1 day | Medium |
| TD-003 | Backend | No custom exception classes; all errors handled by generic handlers | Hard to distinguish error types in monitoring | 4 hours | Low |
| TD-004 | Backend | No caching implementation (cache/ directory empty) | Every request hits DB, no Redis/SQLite cache layer | 3 days | Low |
| TD-005 | Backend | No telemetry/metrics (empty telemetry/, metrics/ dirs) | No observability in production | 2 days | Medium |
| TD-006 | Frontend | No component tests (React Testing Library) | UI regressions not caught by tests | 3 days | Low |
| TD-007 | Frontend | No E2E tests (Playwright/Cypress) | Workflow regressions not caught | 5 days | Low |
| TD-008 | Tests | No async test for SSE/WebSocket | Real-time features untested | 1 day | Low |
| TD-009 | Security | No audit for password service (passlib deprecation warning) | Deprecated `crypt` module used by passlib | 4 hours | Low |
| TD-010 | Database | Some old migration SQL files in src/migrations/ (~13 files) | Confusion about which migrations are active | 2 hours | Low |

## Closed Debt Items

| ID | Area | Description | Resolution | Date |
|----|------|-------------|------------|------|
| TD-011 | Docs | Missing PI-EOS mandatory documentation | Created all 27 docs | 2026-06-25 |
| TD-012 | DTO | Pydantic V2 deprecation warnings | Migrated all 10 DTO files | 2026-06-25 |
| TD-013 | Backend | `on_event` deprecated | Migrated to lifespan | 2026-06-25 |
| TD-014 | DTO | `update_forward_refs` deprecated | Migrated to `model_rebuild` | 2026-06-25 |

## Debt Management Policy
- Critical debt (security/availability): Fix within 24h
- High debt (correctness, data loss): Fix within 1 week
- Medium debt (performance, maintainability): Fix within 1 month
- Low debt (cosmetic, nice-to-have): Fix when working in area
