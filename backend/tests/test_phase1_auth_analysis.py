import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_type,
)
from app.db.session import engine
from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    await engine.dispose()

def unique_email() -> str:
    return f"phase1_{uuid4().hex}@example.com"


async def signup_user(
    client: httpx.AsyncClient,
    *,
    email: str | None = None,
    password: str = "StrongPassword123!",
) -> tuple[dict, str]:
    email = email or unique_email()

    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Phase One Test User",
            "password": password,
        },
    )

    assert response.status_code in {200, 201}, response.text

    return response.json(), password


async def login_user(
    client: httpx.AsyncClient,
    email: str,
    password: str,
) -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Password / JWT security foundation
# ---------------------------------------------------------------------------


def test_password_uses_argon2_and_never_equals_plaintext():
    password = "StrongPassword123!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$argon2")
    assert verify_password(password, password_hash)
    assert not verify_password("WrongPassword123!", password_hash)


def test_access_token_contains_required_claims():
    subject = str(uuid4())

    token = create_access_token(subject)
    payload = decode_token(token)

    assert payload["sub"] == subject
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload


def test_refresh_token_contains_refresh_type():
    subject = str(uuid4())

    token = create_refresh_token(subject)
    payload = verify_token_type(token, "refresh")

    assert payload["sub"] == subject
    assert payload["type"] == "refresh"


def test_access_token_cannot_be_used_as_refresh_token():
    token = create_access_token(str(uuid4()))

    with pytest.raises(ValueError):
        verify_token_type(token, "refresh")


def test_expired_access_token_is_rejected():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "type": "access",
            "iat": now - timedelta(minutes=5),
            "exp": now - timedelta(minutes=1),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)


def test_refresh_token_is_hashed_before_storage():
    raw_token = create_refresh_token(str(uuid4()))

    stored_hash = hash_token(raw_token)

    assert stored_hash != raw_token
    assert len(stored_hash) == 64
    assert stored_hash == hash_token(raw_token)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_registration_creates_user_and_returns_auth_tokens(client):
    email = unique_email()

    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Phase One Registration User",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code in {200, 201}, response.text

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_registration_rejects_duplicate_email(client):
    email = unique_email()

    first = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Duplicate Test User",
            "password": "StrongPassword123!",
        },
    )

    assert first.status_code in {200, 201}, first.text

    second = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Duplicate Test User",
            "password": "StrongPassword123!",
        },
    )

    assert second.status_code in {400, 409}, second.text


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_with_valid_credentials_returns_tokens(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_login_with_invalid_password_is_rejected(client):
    email = unique_email()

    await signup_user(
        client,
        email=email,
        password="CorrectPassword123!",
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Current-user endpoint / authentication
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_users_me_requires_authentication(client):
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_users_me_accepts_valid_access_token(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)
    auth = await login_user(client, email, password)

    response = await client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {auth['access_token']}",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Phase One Test User"


@pytest.mark.asyncio
async def test_users_me_rejects_refresh_token_as_access_token(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)
    auth = await login_user(client, email, password)

    response = await client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {auth['refresh_token']}",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_users_me_rejects_invalid_token(client):
    response = await client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer definitely-not-a-valid-token",
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Refresh-token flow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_returns_new_access_and_refresh_tokens(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)
    auth = await login_user(client, email, password)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": auth["refresh_token"],
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_refresh_rejects_access_token(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)
    auth = await login_user(client, email, password)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": auth["access_token"],
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Logout / session invalidation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_logout_invalidates_refresh_token(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)
    auth = await login_user(client, email, password)

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": auth["refresh_token"],
        },
    )

    assert logout_response.status_code in {200, 204}, logout_response.text

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": auth["refresh_token"],
        },
    )

    assert refresh_response.status_code == 401


# ---------------------------------------------------------------------------
# RBAC / authorization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analysis_endpoint_requires_authentication(client):
    response = await client.post(
        "/api/v1/analysis/url",
        json={
            "url": "https://example.com",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analysis_endpoint_rejects_invalid_access_token(client):
    response = await client.post(
        "/api/v1/analysis/url",
        headers={
            "Authorization": "Bearer invalid-token",
        },
        json={
            "url": "https://example.com",
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# URL analysis validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analysis_endpoint_rejects_malformed_url_for_authenticated_user(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(client, email=email, password=password)
    auth = await login_user(client, email, password)

    response = await client.post(
        "/api/v1/analysis/url",
        headers={
            "Authorization": f"Bearer {auth['access_token']}",
        },
        json={
            "url": "not-a-valid-url",
        },
    )

    assert response.status_code == 422
