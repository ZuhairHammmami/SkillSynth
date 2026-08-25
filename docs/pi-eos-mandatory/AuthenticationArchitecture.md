# Authentication Architecture

## Flow
```
1. User submits credentials → POST /api/auth/token
2. Server verifies bcrypt hash + pepper
3. Checks lockout (5 failed attempts → 15min block)
4. If valid, creates JWT (24h expiry) with profile_id, email, is_admin claims
5. Response: { "access_token": "eyJ...", "token_type": "bearer" }
6. Frontend stores in authToken cookie (httponly: false, secure in prod)
7. All subsequent requests include Authorization: Bearer <token>
```

## Token Structure
```json
{
  "sub": "profile_id",
  "email": "user@example.com",
  "is_admin": false,
  "type": "access",
  "exp": 1700000000,
  "iat": 1700000000
}
```

## SSE Token
- Special short-lived token (1h) via `POST /api/auth/sse-token`
- Used for EventSource connections to `/api/events`

## Password Policy
- Min 8 characters
- Require uppercase, lowercase, digit, special character
- No whitespace
- No common patterns (password, 123456, qwerty, admin, skillsynth, letmein)
- Bcrypt with additional pepper (SHA256 pre-hash layer)

## Registration Flow
```
POST /api/auth/register
  → Validate email (unique), password (policy check)
  → Create User + Profile in DB
  → Auto-assign 'student' role
  → Return profile data (no token — user must login)
```
