# SS-EDS: Security

## Purpose
Document the security architecture: JWT access-token-only auth, account lockout, binary is_admin authorization, rate limiting, CSRF, security headers/CSP/HSTS, and activity_log audit trail.

## Responsibilities
- Issue and verify HS256 JWTs (access 24h; SSE stream token 5 min; password-reset token 30 min — all stateless)
- Enforce password policy and account lockout (5 failures → 15-minute cooldown)
- Apply rate limits via slowapi: global 100/min, auth 10/min, admin 60/min (+ register 5/min, forgot/reset 3/min)
- Configure CSRF double-submit cookie (prod only) and full security-header set
- Record auth and admin actions in activity_log

## Inputs
- OWASP Top 10 requirements
- Credentials from environment (SECRET_KEY, PASSWORD_PEPPER)

## Outputs
- Bearer tokens for API access
- Hardened responses (headers on every response)
- Audit rows in activity_log (category ∈ {audit, auth, system, learning, realtime})

## Dependencies
- 07-backend (auth_service.py, routers/auth.py, limiter.py, middlewares/)
- 10-database (users.is_admin, activity_log)
- 08-frontend / 09-admin (token storage, guards)

## Sequence: Authentication Flow
```
Client → POST /api/auth/token (form-encoded email+password)
  → lockout check (_login_attempts, 5 in 15 min → 429)
  → bcrypt verify (optional SHA-256 pepper pre-hash)
  → record attempt; log to activity_log on success/failure
  → return {access_token, token_type:"bearer"}   # access JWT valid 24h
```

Token renewal is re-authentication; the system issues one token kind per purpose (access, SSE stream, password reset) and nothing else.

## Sequence: Password Reset Flow
```
Client → POST /api/auth/forgot-password (3/min) → always 200
  → stateless signed reset JWT (type=password_reset, sub=email, exp 30 min)
Client → POST /api/auth/reset-password (3/min) with token + new password
  → signature/expiry verified → password updated
```

## State Diagram: Account Lockout
```
[Active] → failed logins accumulate (15-min window) → [5th failure] → [Locked 15 min]
                                                                        ↓ (window passes)
                                                                    [Active]
```

## Rate Limiting (limiter.py, slowapi)
| Scope | Limit | Storage |
|-------|-------|---------|
| Global | 100/minute | In-memory (Redis if REDIS_URL set in prod) |
| Auth router | 10/minute | same |
| Admin routers | 60/minute | same |
| Register | 5/minute | same |
| Forgot/Reset password | 3/minute each | same |

## Authorization
- `get_current_user` decodes the Bearer JWT → user row
- `require_admin` additionally requires `users.is_admin = True` — the only authorization gate; no roles/permissions tables exist

## CSRF Protection (prod only, middlewares/csrf.py)
```
Safe methods: csrf_token cookie rotated per response
Unsafe methods: X-CSRF-Token header must match the csrf_token cookie
GET /api/auth/csrf issues the initial token; that path itself is exempt
```

## Security Headers (middlewares/security.py, every response)
```
X-Content-Type-Options: nosniff · X-Frame-Options: DENY · X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains (+" preload" in prod)
Content-Security-Policy:
  prod: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
        https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;
        img-src 'self' data: https:; connect-src 'self' https://skillsynth.vercel.app;
        frame-ancestors 'none'; form-action 'self'; base-uri 'self'
  dev:  script-src adds 'unsafe-eval' 'unsafe-inline'; connect-src allows localhost:*
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=(), browsing-topics=()
Cross-Origin-Resource-Policy: same-origin · Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

## Password Policy
- Minimum 8 characters (PASSWORD_MIN_LENGTH); complexity validated by auth_service
- Optional pepper: SHA-256(password + PASSWORD_PEPPER) before bcrypt when the env var is set

## Rules
1. All statelessness: no sessions table; revocation = secret rotation or expiry
2. Lockout counters are in-process (thread-safe), reset by restart
3. CSRF enabled only when MODE=prod (CSRF_ENABLED in config/app_settings.py)
4. Every auth event and admin mutation writes an activity_log row
5. SECRET_KEY is mandatory in prod — startup fails without it

## Edge Cases
- Concurrent login attempts share the thread-safe attempt registry
- SSE streams authenticate via the dedicated 5-min token, not the access cookie

## Failure Cases
- Brute force → rate limit at 10/min plus lockout after 5 failures
- Token theft risk mitigated by short-lived SSE/reset tokens; access token lifetime is 24h (documented trade-off)

## Recovery Procedures
1. Rotate SECRET_KEY and restart to invalidate all outstanding tokens
2. Restart the process to clear rate-limit buckets and lockout counters

## Refactoring Strategy
- Candidate improvements (require ADR): token blacklist, HttpOnly cookie mode, 2FA
