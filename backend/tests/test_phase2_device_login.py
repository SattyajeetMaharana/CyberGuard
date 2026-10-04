from __future__ import annotations

from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select

from app.db.models.login_event import LoginEvent
from app.db.session import AsyncSessionLocal, engine
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
    return f"phase2_device_{uuid4().hex}@example.com"


def unique_org_email() -> str:
    return f"phase2_org_{uuid4().hex}@example.com"


@pytest.mark.asyncio
async def test_login_registers_device_and_creates_login_event(client):
    email = unique_email()
    password = "StrongPassword123!"
    device_identifier = f"device-{uuid4().hex}"

    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Phase Two Device User",
            "password": password,
        },
    )
    assert signup.status_code == 201, signup.text

    user_id = UUID(signup.json()["user"]["id"])

    login = await client.post(
        "/api/v1/auth/login",
        headers={"User-Agent": "CyberGuard-Test/1.0"},
        json={
            "email": email,
            "password": password,
            "device_identifier": device_identifier,
            "device_name": "Test Laptop",
            "platform": "Windows",
        },
    )
    assert login.status_code == 200, login.text

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(LoginEvent)
            .where(LoginEvent.user_id == user_id)
            .order_by(LoginEvent.occurred_at.desc())
        )
        login_event = result.scalars().first()

        assert login_event is not None
        assert login_event.user_id == user_id
        assert login_event.login_success is True
        assert login_event.device_id is not None
        assert login_event.user_agent == "CyberGuard-Test/1.0"

    devices = await client.get(
        "/api/v1/devices",
        headers={
            "Authorization": f"Bearer {login.json()['access_token']}",
        },
    )

    assert devices.status_code == 200, devices.text

    device_list = devices.json()
    assert len(device_list) >= 1

    matching_device = next(
        (
            device
            for device in device_list
            if device["device_name"] == "Test Laptop"
        ),
        None,
    )

    assert matching_device is not None
    assert matching_device["platform"] == "Windows"
    assert matching_device["organization_id"] is None
    assert matching_device["is_active"] is True


@pytest.mark.asyncio
async def test_device_organization_isolation(client):
    email = unique_email()
    password = "StrongPassword123!"

    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "full_name": "Device Isolation User",
            "password": password,
        },
    )
    assert signup.status_code == 201, signup.text

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "device_identifier": f"device-{uuid4().hex}",
            "device_name": "Isolation Laptop",
            "platform": "Windows",
        },
    )
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]
    organization_id = uuid4()

    response = await client.get(
        f"/api/v1/devices?organization_id={organization_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_device_cross_organization_isolation(client):
    password = "StrongPassword123!"

    org_a_email = unique_org_email()
    org_b_email = unique_org_email()

    org_a = await client.post(
        "/api/v1/organizations/register",
        json={
            "organization_email": org_a_email,
            "password": password,
            "organization_name": "Phase Two Organization A",
            "organization_identifier": f"ORG-A-{uuid4().hex[:8]}",
        },
    )
    assert org_a.status_code == 201, org_a.text

    org_b = await client.post(
        "/api/v1/organizations/register",
        json={
            "organization_email": org_b_email,
            "password": password,
            "organization_name": "Phase Two Organization B",
            "organization_identifier": f"ORG-B-{uuid4().hex[:8]}",
        },
    )
    assert org_b.status_code == 201, org_b.text

    org_a_data = org_a.json()
    org_b_data = org_b.json()

    # OrganizationRegisterResponse uses "organization_id".
    org_a_id = UUID(org_a_data["organization_id"])
    org_b_id = UUID(org_b_data["organization_id"])

    login_a = await client.post(
        "/api/v1/auth/login",
        json={
            "email": org_a_email,
            "password": password,
            "device_identifier": f"device-org-a-{uuid4().hex}",
            "device_name": "Organization A Laptop",
            "platform": "Windows",
        },
    )
    assert login_a.status_code == 200, login_a.text

    token_a = login_a.json()["access_token"]

    own_devices = await client.get(
        f"/api/v1/devices?organization_id={org_a_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert own_devices.status_code == 200, own_devices.text

    own_device_list = own_devices.json()

    assert any(
        device["device_name"] == "Organization A Laptop"
        for device in own_device_list
    )

    foreign_devices = await client.get(
        f"/api/v1/devices?organization_id={org_b_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert foreign_devices.status_code == 403