"""Auth service — registration, login, tokens and password lifecycle.

Called by routers/auth.py and policies/auth_policy.py
(decode_token). Owns JWT helpers (documented decision: they live here,
not in policies) and ports password rules verbatim from the old
password_service. Auth events are written through engagement_repository.
"""

import hashlib
import os
import secrets
import threading
from datetime import datetime, timedelta, UTC

from jose import jwt
from passlib.context import CryptContext

from backend.dto.auth import PasswordValidator, ProfileOut, RegisterInput
from backend.entities.identity import User
from backend.repositories import assess_repository, engagement_repository
from backend.repositories import identity_repository
from backend.services import settings_schema

SECRET_KEY = os.getenv("SECRET_KEY", "a-secure-default-secret-key-for-development")
ALGORITHM = "HS256"

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_PEPPER = os.getenv("PASSWORD_PEPPER", "")

_login_attempts: dict[str, list[datetime]] = {}
_login_lock = threading.Lock()


def hash_password(password: str) -> str:
    """Bcrypt-hash the peppered password; callers persist the result."""
    if _PEPPER:
        password = hashlib.sha256((password + _PEPPER).encode()).hexdigest()
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time bcrypt verification of the peppered candidate."""
    if _PEPPER:
        plain = hashlib.sha256((plain + _PEPPER).encode()).hexdigest()
    return _pwd_context.verify(plain, hashed)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Policy check returning (ok, message); mirrors PasswordValidator.

    Kept alongside the pydantic validator so non-DTO call sites (admin
    user create/update) enforce identical rules.
    """
    try:
        PasswordValidator.validate(password)
        return True, ""
    except ValueError as exc:
        return False, str(exc)


def create_access_token(data: dict) -> str:
    """HS256 access token with jti; expiry = live session_timeout_hours flag.

    Called by authenticate(); reads the session_timeout_hours flag at
    issuance time (×60 minutes, schema default 24) so a runtime toggle
    changes token lifespan without a restart. Decoded by decode_token.
    """
    hours = settings_schema.get_runtime_flag("session_timeout_hours")
    payload = {**data, "exp": datetime.now(UTC) + timedelta(hours=hours),
               "type": "access", "jti": secrets.token_hex(16)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode any issued token to {} on failure; used by policies +
    reset-password + SSE routers (Task 3)."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        return {}


def create_password_reset_token(email: str) -> str:
    """30-minute signed reset token (type=password_reset, sub=email).

    Statelessly consumed by reset_password; no server-side storage.
    """
    expire = datetime.now(UTC) + timedelta(minutes=30)
    return jwt.encode({"exp": expire, "sub": email,
                       "type": "password_reset",
                       "jti": secrets.token_hex(16)},
                      SECRET_KEY, algorithm=ALGORITHM)


def create_sse_token(user_id: int) -> str:
    """5-minute SSE stream token; /auth/sse-token endpoint (Task 3)."""
    expire = datetime.now(UTC) + timedelta(minutes=5)
    return jwt.encode({"exp": expire, "sub": str(user_id), "type": "sse",
                       "jti": secrets.token_hex(16)}, SECRET_KEY, algorithm=ALGORITHM)


def build_profile_out(db, user: User) -> ProfileOut:
    """Serialize a user with the synthesized flat skill_profile dict.

    Called by auth routers (/auth/me, /auth/register); the dict comes
    from assess_repository.get_skill_profile ({skills.name: level}).
    """
    out = ProfileOut.model_validate(user)
    out.skill_profile = assess_repository.get_skill_profile(db, user.id)
    return out


def log_auth(db, user_id: int | None, email: str, success: bool,
             ip: str | None) -> None:
    """Persist an auth activity row and broadcast it to admin streams.
    Wraps engagement_repository.write then send_admin_activity so the
    admin audit feed's sse:activity prepend stays live."""
    from backend.events.publisher import send_admin_activity
    row = engagement_repository.write(
        db, category="auth", action="login" if success else "login_failed",
        user_id=user_id, entity_type="user", entity_id=user_id,
        data={"email": email, "success": success}, ip_address=ip,
    )
    send_admin_activity(row)


class AuthService:
    """Static façade kept for router import compatibility (Task 3)."""

    @staticmethod
    def check_login_allowed(email: str) -> tuple[bool, str | None]:
        """Lockout gate: True unless the live attempt limit is exceeded.

        Reads account_lockout_attempts/lockout_minutes at call time (schema
        defaults 5/15) so a runtime toggle applies immediately. Routers map
        the failure to 429; authenticate() also enforces it defensively.
        """
        max_attempts = settings_schema.get_runtime_flag("account_lockout_attempts")
        window_minutes = settings_schema.get_runtime_flag("lockout_minutes")
        with _login_lock:
            now = datetime.now(UTC)
            cutoff = now - timedelta(minutes=window_minutes)
            attempts = [t for t in _login_attempts.get(email, []) if t > cutoff]
            _login_attempts[email] = attempts
            locked = len(attempts) >= max_attempts
        if locked:
            return False, (f"Account locked due to {max_attempts} failed "
                           f"attempts. Try again in {window_minutes} minutes.")
        return True, None

    @staticmethod
    def record_login_attempt(email: str, success: bool) -> None:
        """Clear attempts on success, append timestamp on failure."""
        with _login_lock:
            if success:
                _login_attempts.pop(email, None)
            else:
                _login_attempts.setdefault(email, []).append(datetime.now(UTC))

    @staticmethod
    def register(db, data: RegisterInput) -> tuple[User | None, str | None]:
        """Create a user after uniqueness + strength checks.

        Returns (user, None) or (None, error_message); routers map the
        error to HTTP 400. Hashes via hash_password (peppered bcrypt).
        """
        if identity_repository.get_by_email(db, data.email):
            return None, "Email already registered"
        valid, msg = validate_password_strength(data.password)
        if not valid:
            return None, msg
        user = identity_repository.create(
            db, email=data.email, hashed_password=hash_password(data.password),
            full_name=data.full_name or "", is_admin=False)
        return user, None

    @staticmethod
    def update_profile(db, user_id: int, fields: dict) -> User | None:
        """Apply ProfileUpdate dump; returns updated user or None."""
        user = identity_repository.get_by_id(db, user_id)
        if not user:
            return None
        return identity_repository.update_fields(
            db, user, {k: v for k, v in fields.items() if v is not None})

    @staticmethod
    def change_password(db, user: User, current: str, new: str) -> tuple[bool, str]:
        """Verify current password then rotate; (ok, message) result."""
        if not verify_password(current, user.hashed_password):
            return False, "Incorrect current password"
        valid, msg = validate_password_strength(new)
        if not valid:
            return False, msg
        identity_repository.update_password(db, user.id, hash_password(new))
        return True, "Password updated successfully"

    @staticmethod
    def request_reset(db, email: str) -> dict:
        """Stateless password-reset issuance; always-200 payload shape.

        Returns {"message": ...} unchanged for unknown emails (no
        enumeration); when the account exists the signed 30-minute
        reset JWT is included as "reset_token" so the flow works
        without the removed email layer. An auth activity row is
        written via engagement_repository.write(db, ...) and broadcast
        to the admin channel.
        """
        from backend.events.publisher import send_admin_activity
        payload = {"message": ("If an account with this email exists, a "
                               "password reset link has been sent.")}
        user = identity_repository.get_by_email(db, email)
        if user:
            payload["reset_token"] = create_password_reset_token(user.email)
            row = engagement_repository.write(
                db, category="auth", action="password_reset_requested",
                user_id=user.id, entity_type="user", entity_id=user.id,
                data={"email": email}, ip_address=None)
            send_admin_activity(row)
        return payload

    @staticmethod
    def reset_password(db, token_str: str, new_password: str) -> tuple[bool, str]:
        """Validate signature+purpose+expiry of a reset JWT, then rotate.

        Returns (ok, message); routers map failures to 400 matching the
        old contract. Expiry surfaces as an invalid token via decode.
        """
        payload = decode_token(token_str)
        if not payload or payload.get("type") != "password_reset" \
                or not payload.get("sub"):
            return False, "Invalid token"
        user = identity_repository.get_by_email(db, payload["sub"])
        if not user:
            return False, "User not found"
        valid, msg = validate_password_strength(new_password)
        if not valid:
            return False, msg
        identity_repository.update_password(db, user.id, hash_password(new_password))
        return True, "Password has been reset successfully."

    @staticmethod
    def authenticate(db, email: str, password: str,
                     ip: str | None) -> tuple[User | None, str | None]:
        """Lockout-checked credential verification.

        Returns (user, None) on success — the caller builds the bearer
        token from user.email/user.id via create_access_token — else
        (None, message) where lockout messages start with "Account locked".
        Writes an auth activity row either way.
        """
        allowed, lock_msg = AuthService.check_login_allowed(email)
        if not allowed:
            return None, lock_msg
        user = identity_repository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            AuthService.record_login_attempt(email, False)
            log_auth(db, None, email, False, ip)
            return None, "Incorrect email or password"
        AuthService.record_login_attempt(email, True)
        log_auth(db, user.id, email, True, ip)
        return user, None


# Module-level façade (brief signatures): thin delegates to AuthService.
def register(db, data: RegisterInput):
    """See AuthService.register; returns (user|None, error|None)."""
    return AuthService.register(db, data)


def authenticate(db, email: str, password: str, ip: str | None):
    """See AuthService.authenticate; returns (user|None, error|None)."""
    return AuthService.authenticate(db, email, password, ip)


def update_profile(db, user_id: int, fields: dict):
    """See AuthService.update_profile."""
    return AuthService.update_profile(db, user_id, fields)


def change_password(db, user: User, current: str, new: str):
    """See AuthService.change_password; returns (ok, message)."""
    return AuthService.change_password(db, user, current, new)


def request_reset(db, email: str) -> dict:
    """See AuthService.request_reset; returns the always-200 payload."""
    return AuthService.request_reset(db, email)


def reset_password(db, token_str: str, new_password: str):
    """See AuthService.reset_password; returns (ok, message)."""
    return AuthService.reset_password(db, token_str, new_password)
