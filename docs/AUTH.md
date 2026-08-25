# Authentication & Security

## Auth Flow

```
Login Page → POST /api/auth/token (email+password)
  → Backend verifies bcrypt hash
  → Returns JWT (HS256, 7 day expiry, payload: {sub: email, profile_id: id})
  → Frontend stores as 'authToken' cookie (js-cookie, SameSite=strict, secure in prod)
  → Fetches GET /api/auth/users/me (Axios interceptor auto-adds Bearer header)
  → Zustand isAuthenticated = true
  → Redirect to /dashboard or /admin/dashboard
```

## JWT Details

| Property | Value |
|----------|-------|
| Algorithm | HS256 (HMAC-SHA256) |
| Secret | `SECRET_KEY` env var (prod: required, dev: hardcoded fallback) |
| Access token expiry | **7 days** (10080 min) |
| Reset token expiry | 15 min |
| SSE token expiry | 5 min |
| Library | `python-jose` + `passlib[bcrypt]` |
| Refresh tokens | **None** |
| Token blacklist | **None** (tokens valid until expiry even after logout) |

## Cookie Configuration

```typescript
Cookies.set('authToken', token, {
  expires: 7,             // days
  path: '/',
  sameSite: 'strict',     // CSRF protection
  secure: prod,           // HTTPS only in production
  // HttpOnly: NOT set — accessible to JS
});
```

## Route Protection

### Frontend — Edge Middleware (`middleware.ts`)
- Reads `authToken` cookie
- Protected → redirect to `/login?redirect=<path>`
- Auth routes (login/register) → redirect to `/dashboard` if authenticated
- Sets `NEXT_LOCALE` cookie

### Frontend — Client Guards
- `AuthGuard`: Zustand `isAuthenticated` check + skeleton
- `AdminGuard`: `user.is_admin` check + redirect

### Backend — FastAPI Dependencies
- `get_current_user`: Extracts Bearer token, decodes JWT, fetches Profile
- `get_current_admin_user`: Wraps above + `is_admin == True` check
- `require_permission(perm)`: Checks role permissions or admin override

## Admin System

| Creation Method | Credentials |
|----------------|-------------|
| Auto on startup | `ADMIN_EMAIL` (default `admin@skillsynth.io`) + `ADMIN_PASSWORD` env |
| Standalone script | `python src/backend/create_admin.py` → `admin@skillsynth.com` / `adminpassword123` |
| Admin API | `POST /api/admin/users` with `is_admin=true` |

**Roles**: `Role` model with `permissions` (JSON string array). Admin auto-grants all.

## Rate Limiting (slowapi)

| Endpoint | Limit |
|----------|-------|
| POST /api/auth/register | 5/min |
| POST /api/auth/token | 10/min |
| POST /api/auth/forgot-password | 3/min |
| POST /api/auth/request-password-reset | 3/min |
| POST /api/auth/reset-password | 3/min |

All other endpoints: **unlimited**.

## Security Headers (`main.py`)

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'` (prod only)

## Password Policy

- Min 8 characters, ≥1 uppercase, ≥1 digit
- Hashed with bcrypt via `passlib`
- Reset token: 15-min JWT (type: "reset")

## Security Gaps

- **No HttpOnly cookie** — JWT accessible to JS (XSS risk)
- **No token revocation** — logged-out tokens valid for 7 days
- **Long token expiry** — 7 days without rotation
- **No rate limiting on most endpoints** — admin ops, path generation, etc.
- **No CSRF token** — mitigated by SameSite=Strict only
- **No login attempt tracking** — IP rate limiting only, no account lockout
- **Dev secret hardcoded** — `"a-secure-default-secret-for-development"` fallback
- **No 2FA/MFA**
- **Supabase auth unused** — `@supabase/ssr` installed, `supabase.ts` client exists, but not wired
