from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.db.models.credential import Credential
from app.db.models.refresh_token import RefreshToken
from app.db.models.session import Session
from app.db.models.user import User


async def signup_user(
    db: AsyncSession,
    email: str,
    full_name: str,
    password: str,
) -> User:
    """Create a user and securely store the Argon2 password hash."""

    result = await db.execute(
        select(User).where(User.email == email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise ValueError("Email already registered")

    user = User(
        email=email,
        full_name=full_name,
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    await db.flush()

    credential = Credential(
        user_id=user.id,
        password_hash=hash_password(password),
        is_active=True,
        password_changed_at=datetime.now(timezone.utc),
    )

    db.add(credential)

    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user using the stored Argon2 password hash."""

    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    credential_result = await db.execute(
        select(Credential).where(
            Credential.user_id == user.id,
            Credential.is_active.is_(True),
        )
    )

    credential = credential_result.scalar_one_or_none()

    if credential is None:
        return None

    if not verify_password(
        password,
        credential.password_hash,
    ):
        return None

    return user


async def create_session_and_refresh_token(
    db: AsyncSession,
    user: User,
    *,
    device_id=None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> tuple[Session, str]:
    """
    Create a server-side session and persist only a hash
    of the refresh token.
    """

    now = datetime.now(timezone.utc)

    session_expires_at = now + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    session = Session(
        user_id=user.id,
        device_id=device_id,
        expires_at=session_expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
    )

    db.add(session)
    await db.flush()

    refresh_token = create_refresh_token(str(user.id))

    stored_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=session_expires_at,
        is_active=True,
        session_id=session.id,
    )

    db.add(stored_refresh_token)

    await db.commit()
    await db.refresh(session)

    return session, refresh_token


async def refresh_session(
    db: AsyncSession,
    refresh_token: str,
) -> tuple[User, Session, str] | None:
    """
    Validate a refresh token against its JWT claims and
    server-side hashed token record, then rotate it.
    """

    from app.core.security import verify_token_type

    try:
        payload = verify_token_type(
            refresh_token,
            "refresh",
        )
    except Exception:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    token_hash = hash_token(refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
            RefreshToken.is_active.is_(True),
            RefreshToken.revoked_at.is_(None),
        )
    )

    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        return None

    now = datetime.now(timezone.utc)

    if stored_token.expires_at <= now:
        stored_token.is_active = False
        await db.commit()
        return None

    session = None

    if stored_token.session_id is not None:
        session_result = await db.execute(
            select(Session).where(
                Session.id == stored_token.session_id,
                Session.user_id == user_id,
                Session.is_active.is_(True),
                Session.revoked_at.is_(None),
            )
        )

        session = session_result.scalar_one_or_none()

    if session is None or session.expires_at <= now:
        stored_token.is_active = False
        await db.commit()
        return None

    user_result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
        )
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        return None

    # Rotate the refresh token.
    stored_token.revoked_at = now
    stored_token.is_active = False

    new_refresh_token = create_refresh_token(str(user.id))

    new_stored_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token),
        expires_at=session.expires_at,
        is_active=True,
        session_id=session.id,
    )

    db.add(new_stored_token)
    await db.commit()

    return user, session, new_refresh_token


async def revoke_refresh_token(
    db: AsyncSession,
    refresh_token: str,
) -> bool:
    """Revoke a refresh token and its associated session."""

    token_hash = hash_token(refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_active.is_(True),
            RefreshToken.revoked_at.is_(None),
        )
    )

    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        return False

    now = datetime.now(timezone.utc)

    stored_token.revoked_at = now
    stored_token.is_active = False

    if stored_token.session_id is not None:
        session_result = await db.execute(
            select(Session).where(
                Session.id == stored_token.session_id,
                Session.is_active.is_(True),
            )
        )

        session = session_result.scalar_one_or_none()

        if session is not None:
            session.revoked_at = now
            session.is_active = False

    await db.commit()

    return True


def generate_access_token(user_id: str) -> str:
    """Generate an access token for an authenticated user."""
    return create_access_token(subject=user_id)


def generate_refresh_token(user_id: str) -> str:
    """Generate a refresh token for an authenticated user."""
    return create_refresh_token(subject=user_id)