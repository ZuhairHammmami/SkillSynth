# Non-Functional Requirements

## Performance Budgets
| Metric | Target | Measurement |
|--------|--------|-------------|
| API P95 Latency | <200ms | /api/learning/graph, /api/analytics/dashboard |
| Auth Latency P95 | <50ms | /api/auth/token, /api/auth/me |
| SSE Event Delivery | <100ms | From publish to client receipt |
| Frontend LCP | <1.5s | Lighthouse, all routes |
| Frontend TTFB | <500ms | Next.js server response |
| Bundle Size (shared) | <250kB gzip | next build output |
| DB Query P95 | <30ms | Direct SQLite/PostgreSQL |
| Concurrency | 100 simultaneous users | FastAPI with 10 pool connections |

## Availability & Reliability
| Metric | Target |
|--------|--------|
| Uptime | 99.9% (8.76h/year max) |
| Error Rate | <0.1% of all requests |
| Recovery Time (RTO) | <15 minutes |
| Recovery Point (RPO) | <5 minutes (DB) |

## Security Requirements
| Requirement | Implementation |
|-------------|---------------|
| Auth | JWT Bearer tokens, 24h session, refresh rotation |
| Password Policy | 8+ chars, uppercase, lowercase, digit, special, no common patterns |
| Lockout | 5 failed attempts → 15min lockout |
| CSRF | Double-submit cookie pattern (prod only) |
| Rate Limiting | 100/min global, 10/min auth, 60/min admin |
| Headers | CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| RBAC | 6 roles, 51 permissions, route-level guards |

## Scalability
| Dimension | Current | Target |
|-----------|---------|--------|
| Users | 5 seeded | 10,000 |
| Skills | 102 | 500+ |
| Concurrent Paths | 5 | 10,000 |
| Resources | 87 | 5,000+ |

## Data Integrity
- Strict 3NF — no JSON bridge columns
- Foreign keys with CASCADE/SET NULL policies
- Soft delete on users, files via `deleted_at`
- All queries filter `deleted_at IS NULL`
- Backups every 15 minutes (WAL mode)

## Compliance
- GDPR: Data export, account deletion, audit logs
- WCAG AA: Keyboard nav, screen reader, contrast ratios
- AR/EN Parity: 100% translation coverage, dynamic RTL switching
