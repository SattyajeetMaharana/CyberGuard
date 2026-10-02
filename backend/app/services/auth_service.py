from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User


async def signup_user(
    db: AsyncSession,
    email: str,
    full_name: str,
    password: str,
) -> User:
    result = await db.execute(
        select(User).where(User.email == email)
    )

    if result.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email,
        full_name=full_name,
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if not user:
        return None

    return user


def generate_access_token(user_id: str) -> str:
    return create_access_token(
        subject=user_id,
        token_type="access",
    )