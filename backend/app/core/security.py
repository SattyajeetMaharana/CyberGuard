from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings


password_hasher = PasswordHasher()


# ---------------------------------------------------------------------------
# Password security
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against an Argon2 password hash."""
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


# ---------------------------------------------------------------------------
# Token security
# ---------------------------------------------------------------------------

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
        "jti": str(uuid4()),
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
    """Create a long-lived refresh token."""
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and cryptographically validate a JWT.

    PyJWT validates the signature and expiration (`exp`) during decoding.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_token_type(
    token: str,
    expected_type: str,
) -> dict[str, Any]:
    """Validate a JWT and ensure it is the expected token type."""
    payload = decode_token(token)

    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")

    if not payload.get("sub"):
        raise ValueError("Invalid token subject")

    return payload


# ---------------------------------------------------------------------------
# Refresh-token storage security
# ---------------------------------------------------------------------------

def hash_token(token: str) -> str:
    """
    Hash a refresh token before storing it in the database.

    The raw refresh token must never be stored in the database.
    """
    return sha256(token.encode("utf-8")).hexdigest()