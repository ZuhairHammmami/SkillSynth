# Security Architecture

## Authentication
- **Protocol**: JWT Bearer tokens (access + refresh rotation)
- **Algorithm**: HS256 via python-jose
- **Session**: 24h timeout, cookie-based (authToken)
- **Password Hashing**: bcrypt with pepper (SHA256 pre-hash)
- **Lockout**: 5 failed attempts → 15-minute lockout

## Authorization (RBAC)
- **6 Roles**: super_admin, admin, editor, content_manager, student, viewer
- **51 Permissions**: granular resource:action tuples
- **Admin Guard**: `get_current_admin_user()` dependency on all admin routers
- **Permission Check**: `require_permission()` factory function

## Middleware Stack
| Middleware | Purpose |
|-----------|---------|
| CORS | Allow origins, credentials, specific headers |
| Compression | gzip responses >1KB |
| Security Headers | CSP, HSTS, XFO, X-Content-Type-Options |
| CSRF | Double-submit cookie pattern (prod only) |

## Rate Limiting (slowapi)
| Scope | Rate |
|-------|------|
| Global | 100/min |
| Auth | 10/min |
| Admin | 60/min |

## OWASP Top 10 Mitigations
| Risk | Mitigation |
|------|-----------|
| Injection (A1) | SQLAlchemy parameterized queries, Pydantic validation |
| Broken Auth (A2) | JWT with rotation, bcrypt + pepper, rate limiting |
| XSS (A3) | CSP headers, React's auto-escaping, sanitization |
| Broken Access Control (A4) | RBAC, `get_current_admin_user` on all admin routes |
| CSRF (A8) | Double-submit cookie pattern |
| XXE (A5) | JSON-only API, no XML parsing |
| Security Misconfiguration (A6) | CORS whitelist, HSTS, CSP |
