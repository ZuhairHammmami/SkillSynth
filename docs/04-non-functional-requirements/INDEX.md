# SS-EDS: Non-Functional Requirements

## Purpose
Define performance, security, scalability, availability, and maintainability targets for SkillSynth. Establishes SLAs and quality gates.

## Responsibilities
- Set and enforce performance budgets (API response times, Lighthouse scores)
- Define security baselines (JWT, rate limiting, headers)
- Track availability and error budgets
- Monitor database query performance (N+1 prevention)

## Inputs
- Architecture decisions (06-architecture)
- Infrastructure constraints (17-deployment)
- Security audit findings (14-security)

## Outputs
- Performance budget document
- SLA definitions
- Monitoring thresholds (18-monitoring)
- Error budget policy

## Dependencies
- 15-performance (performance monitoring)
- 14-security (security requirements)
- 18-monitoring (observability)
- 16-testing (load testing)

## Sequence: NFR Validation Flow
```
Develop → Self-Review → PR → CI Checks → Performance Test → Security Scan → Release
                                    ↓                  ↓
                              Fails NFR          Fails Threshold
                                    ↓                  ↓
                              Block Merge       Rollback / Fix
```

## State Diagram: Performance Budget Status
```
[Green] → [Warning (80% of budget)] → [Critical (95%)] → [Violation]
```

## ERD References
- 11 composite indexes on SQLAlchemy models
- events table for latency tracking

## Rules
1. Lighthouse must be 100/100/100/100 on every page
2. API endpoints must respond < 50ms p95 (dev mode allowance: < 200ms)
3. CLS must be 0.00
4. TTFB < 200ms (production build)
5. Zero `tsc --noEmit` errors
6. Zero `next lint` errors (warnings allowed if documented)
7. No N+1 queries in any API endpoint

## Examples
- /api/auth/me: 3.5ms
- /api/admin/users: 9.4ms
- /api/analytics/dashboard: 21.4ms
- /api/paths/: 17.7ms

## Edge Cases
- Database connection pool exhaustion under load
- SSE connection limits with many concurrent users
- Rate limiting preventing legitimate admin bulk operations

## Failure Cases
- Lighthouse score drops → immediate flag on CI
- Response time exceeds 1s p95 → incident
- N+1 query introduced → blocked in code review

## Recovery Procedures
1. Identify bottleneck via profiling
2. Apply index, cache, or query optimization
3. Verify fix in staging before production

## Refactoring Strategy
- Performance regression tests in CI
- Quarterly Lighthouse audit on all routes
- Monthly database query plan review
