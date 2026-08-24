"""Auth policy — JWT → user resolution and the admin gate.

Called by every protected router (Task 3). JWT encode/decode helpers
live in services/auth_service (documented decision); this module only
maps a decoded `sub` email onto a users row.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.entities.identity import User
from backend.services.auth_service import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def _unauthorized() -> HTTPException:
    """Shared 401 shape with the WWW-Authenticate challenge header."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    """Resolve the bearer token to a users row via JWT sub=email.

    Raises 401 when decoding fails or the account no longer exists;
    called directly by user-facing routers and by require_admin below.
    """
    payload = decode_token(token)
    email = payload.get("sub") if payload.get("type") in ("access", None) else None
    if not email:
        raise _unauthorized()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise _unauthorized()
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """403 unless the resolved user is_admin; sole privilege gate now
    that roles were removed. Alias kept for old router imports."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have administrative privileges",
        )
    return current_user


# Backwards-compatible alias so Task 3 router diffs stay mechanical.
get_current_admin_user = require_admin
