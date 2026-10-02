from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from app.core.config import settings


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against an Argon2 hash."""
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """Create a signed JWT token."""
    now = datetime.now(timezone.utc)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(subject: str) -> str:
    """Create a short-lived access token."""
    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )


def create_refresh_token(subject: str) -> str:
    """Create a longer-lived refresh token."""
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_token_type(token: str, expected_type: str) -> dict[str, Any]:
    """Decode a token and ensure it has the expected token type."""
    payload = decode_token(token)

    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")

    if not payload.get("sub"):
        raise ValueError("Invalid token subject")

    return payload
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False