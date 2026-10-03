from __future__ import annotations

from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio

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
    return f"phase1_event_{uuid4().hex}@example.com"


async def signup_user(
    client: httpx.AsyncClient,
    *,
    email: str | None = None,
) -> tuple[dict, str]:
    email = email or unique_email()
    password = "StrongPassword123!"

    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Phase One Event User",
            "password": password,
        },
    )

    assert response.status_code == 201, response.text

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
# Core Event API
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_event_endpoint_requires_authentication(client):
    response = await client.post(
        "/api/v1/events",
        json={
            "event_type": "TEST_EVENT",
            "source_type": "test",
            "payload": {
                "message": "unauthenticated event",
            },
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_user_can_create_core_event(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(
        client,
        email=email,
    )

    auth = await login_user(
        client,
        email,
        password,
    )

    response = await client.post(
        "/api/v1/events",
        headers={
            "Authorization": f"Bearer {auth['access_token']}",
        },
        json={
            "event_type": "LOGIN_ACTIVITY",
            "source_type": "authentication",
            "payload": {
                "authentication_method": "password",
                "test": True,
            },
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["event_id"]
    assert data["context_id"]
    assert data["user_id"]
    assert data["device_id"] is None

    assert data["event_type"] == "LOGIN_ACTIVITY"
    assert data["source_type"] == "authentication"

    assert data["payload"]["authentication_method"] == "password"
    assert data["payload"]["test"] is True

    UUID(data["event_id"])
    UUID(data["context_id"])
    UUID(data["user_id"])


@pytest.mark.asyncio
async def test_event_user_and_context_are_derived_from_authenticated_user(
    client,
):
    first_email = unique_email()
    second_email = unique_email()
    password = "StrongPassword123!"

    first_signup, _ = await signup_user(
        client,
        email=first_email,
    )

    second_signup, _ = await signup_user(
        client,
        email=second_email,
    )

    first_user_id = first_signup["user"]["id"]
    second_user_id = second_signup["user"]["id"]

    first_auth = await login_user(
        client,
        first_email,
        password,
    )

    malicious_user_id = second_user_id
    malicious_context_id = str(uuid4())

    response = await client.post(
        "/api/v1/events",
        headers={
            "Authorization": f"Bearer {first_auth['access_token']}",
        },
        json={
            "event_type": "CONTEXT_TEST",
            "source_type": "test",
            "payload": {
                "owner": "first-user",
            },

            # These fields are intentionally not part of
            # CoreEventCreate. They simulate an attempt to
            # impersonate another user's identity/context.
            "user_id": malicious_user_id,
            "context_id": malicious_context_id,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    # The API must derive the event owner from the authenticated
    # user rather than trusting a client-supplied user_id.
    assert data["user_id"] == first_user_id
    assert data["user_id"] != malicious_user_id

    # The API must derive the security context from the
    # authenticated user's active personal context.
    assert data["context_id"]
    assert data["context_id"] != malicious_context_id

    assert data["event_type"] == "CONTEXT_TEST"
    assert data["payload"]["owner"] == "first-user"


@pytest.mark.asyncio
async def test_event_defaults_occurred_at_when_not_supplied(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(
        client,
        email=email,
    )

    auth = await login_user(
        client,
        email,
        password,
    )

    response = await client.post(
        "/api/v1/events",
        headers={
            "Authorization": f"Bearer {auth['access_token']}",
        },
        json={
            "event_type": "TIMESTAMP_TEST",
            "source_type": "test",
            "payload": {},
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["occurred_at"]
    assert data["event_id"]
    assert data["context_id"]
    assert data["user_id"]


@pytest.mark.asyncio
async def test_event_preserves_supplied_timestamp(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(
        client,
        email=email,
    )

    auth = await login_user(
        client,
        email,
        password,
    )

    occurred_at = "2026-01-15T10:30:00+00:00"

    response = await client.post(
        "/api/v1/events",
        headers={
            "Authorization": f"Bearer {auth['access_token']}",
        },
        json={
            "event_type": "TIMESTAMP_TEST",
            "source_type": "test",
            "payload": {
                "timestamp_check": True,
            },
            "occurred_at": occurred_at,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["occurred_at"].startswith(
        "2026-01-15T10:30:00"
    )


@pytest.mark.asyncio
async def test_event_rejects_empty_event_type(client):
    email = unique_email()
    password = "StrongPassword123!"

    await signup_user(
        client,
        email=email,
    )

    auth = await login_user(
        client,
        email,
        password,
    )

    response = await client.post(
        "/api/v1/events",
        headers={
            "Authorization": f"Bearer {auth['access_token']}",
        },
        json={
            "event_type": "",
            "source_type": "test",
            "payload": {},
        },
    )

    assert response.status_code == 422