from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SignupRequest,
)
from app.services.auth_service import (
    authenticate_user,
    create_session_and_refresh_token,
    generate_access_token,
    refresh_session,
    revoke_refresh_token,
    signup_user,
)
from app.services.device_service import register_device
from app.services.event_service import create_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _auth_response(
    user,
    access_token: str,
    refresh_token: str,
) -> AuthResponse:
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user,
    )


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    payload: SignupRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await signup_user(
            db=db,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    session, refresh_token = await create_session_and_refresh_token(
        db=db,
        user=user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    access_token = generate_access_token(str(user.id))

    return _auth_response(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    device = None

    if payload.device_identifier is not None:
        device = await register_device(
            db=db,
            user_id=user.id,
            device_identifier=payload.device_identifier,
            device_name=payload.device_name,
            platform=payload.platform,
        )

    session, refresh_token = await create_session_and_refresh_token(
        db=db,
        user=user,
        device_id=device.id if device else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    await create_event(
        db=db,
        event_type="LOGIN_SUCCESS",
        source_type="authentication",
        user_id=user.id,
        device_id=device.id if device else None,
        payload={
            "session_id": str(session.id),
            "authentication_method": "password",
        },
    )

    await db.commit()

    access_token = generate_access_token(str(user.id))

    return _auth_response(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await refresh_session(
        db=db,
        refresh_token=payload.refresh_token,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, _, new_refresh_token = result

    access_token = generate_access_token(str(user.id))

    return _auth_response(
        user=user,
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    await revoke_refresh_token(
        db=db,
        refresh_token=payload.refresh_token,
    )

    return None