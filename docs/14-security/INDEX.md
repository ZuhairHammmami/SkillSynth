# SS-EDS: Security

## Purpose
Document the authentication, authorization, and security architecture. Covers JWT with refresh token rotation, account lockout, RBAC, rate limiting, CSRF, CSP, HSTS, and audit logging.

## Responsibilities
- Implement JWT access/refresh/sse/password-reset tokens (HS256, python-jose)
- Enforce password complexity (min 8, upper, lower, digit, special, no common patterns)
- Implement account lockout after 5 failed attempts (15-min reset)
- Apply rate limiting: global 100/min, auth 10/min, admin 60/min
- Configure CSRF double-submit cookie (prod-only)
- Apply security headers (CSP, HSTS, XFO, Referrer-Policy, Permissions-Policy)
- Log all auth and admin actions via AuditService

## Inputs
- Security best practices (OWASP Top 10)
- Compliance requirements
- Threat model analysis

## Outputs
- JWT tokens (24h access, 30d refresh, 5min SSE, 15min reset)
- Rate-limited endpoints
- Security headers on all responses
- RBAC permission checks
- Audit log entries (events table + JSON logger)

## Dependencies
- 07-backend (auth_service.py, auth_router.py, middlewares/)
- 10-database (profiles table, roles table)
- 08-frontend (middleware.ts, AuthGuard)

## Sequence: Authentication Flow
```
Client → POST /api/auth/token (email + password)
  → Backend checks _is_locked_out (5 failed attempts in 15 min?)
  → 429 if locked, "Try again in 15 minutes"
  → Verifies bcrypt hash (with pepper)
  → Records attempt (success/failure)
  → AuditService.log_auth (login / login_failed)
  → Creates access token (24h) + refresh token (30d)
  → Returns {access_token, token_type, expires_in}
```

## Sequence: Token Refresh Flow
```
Client → POST /api/auth/refresh (refresh_token)
  → AuthService.rotate_refresh_token(old)
  → Validates JWT, checks type="refresh"
  → Deletes old JTI from _refresh_tokens
  → Creates new access token + new refresh token
  → Returns new tokens
```

## State Diagram: Account Lockout
```
[Active] → Failed Login → [1 Attempt] → ... → [5 Failed in 15 min] → [Locked]
                                                                          ↓
                                                              [Wait 15 min or Admin Unlock]
                                                                          ↓
                                                                      [Active]
```

## Rate Limiting Configuration (limiter.py)
| Scope | Limit | Storage |
|-------|-------|---------|
| Global | 100/minute | Redis (prod) / InMemory (dev) |
| Auth | 10/minute | Redis / InMemory |
| Admin | 60/minute | Redis / InMemory |
| Register | 5/minute | slowapi decorator |
| Forgot Password | 3/minute | slowapi decorator |

## CSRF Protection (prod only)
```
Safe methods (GET, HEAD, OPTIONS, TRACE): cookie rotated on each response
Unsafe methods (POST, PUT, DELETE): X-CSRF-Token header must match csrf_token cookie
+ GET /api/auth/csrf → returns token + sets cookie
```

## Content Security Policy (prod)
```
default-src 'self'
script-src 'self'
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com
font-src 'self' https://fonts.gstatic.com
img-src 'self' data: https:
connect-src 'self' https://skillsynth.vercel.app
frame-ancestors 'none'
form-action 'self'
base-uri 'self'
```

## Security Headers (all responses)
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
Cross-Origin-Resource-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

## Password Policy
- Min 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character
- No whitespace
- No common patterns (password, 123456, qwerty, admin)
- Peppered (SHA-256 + PASSWORD_PEPPER) before bcrypt

## Audit Logging (AuditService)
```python
AuditService.log_auth(profile_id, email, success, ip)
AuditService.log_permission_violation(profile_id, email, "users:create", ip)
AuditService.log_admin_action(admin_id, email, "user.delete", "profile", user_id, details, ip)
```

## Rules
1. Passwords: bcrypt + pepper. Min 8, upper, lower, digit, special.
2. Account lockout: 5 failed attempts → 15 min cooldown
3. Rate limits: global 100/min, auth 10/min, admin 60/min
4. CSRF double-submit cookie enabled in prod only
5. All auth/admin events logged via AuditService
6. JWT secret key configurable via SECRET_KEY env var

## Edge Cases
- Concurrent login attempts tracked via thread-safe _login_lock
- Admin with is_admin=True bypasses RBAC permission checks
- CSRF exempt for /api/auth/csrf endpoint only

## Failure Cases
- SECRET_KEY missing in prod → app refuses to start
- Brute force → rate limited at 10/min + lockout after 5
- XSS if attacker accesses cookie (no HttpOnly — intentional, known gap)

## Recovery Procedures
1. Rotate SECRET_KEY: AuthService.rotate_secret_key(new_key)
2. Clear rate limiter state via server restart
3. Admin manually unlocks account (clear _login_attempts dict)

## Refactoring Strategy
- Add token blacklist (Redis) for immediate revocation
- Implement HttpOnly cookie option as configurable
- Add 2FA/MFA support
- Migrate to full Redis-backed distributed rate limiting
