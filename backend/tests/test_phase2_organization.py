from __future__ import annotations

from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select

from app.db.models.invitation import Invitation
from app.db.models.role import Role
from app.db.models.user import User
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


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}@example.com"


async def register_org(
    client: httpx.AsyncClient,
    prefix: str = "phase2",
) -> tuple[dict, str]:
    email = unique_email(prefix)
    password = "StrongPassword123!"

    response = await client.post(
        "/api/v1/organizations/register",
        json={
            "organization_email": email,
            "password": password,
            "organization_name": f"Organization {uuid4().hex[:8]}",
            "organization_identifier": f"ID-{uuid4().hex[:12]}",
            "proof_type": "TEST",
            "proof_reference": "TEST-REFERENCE",
        },
    )

    assert response.status_code == 201, response.text

    return response.json(), password


async def login(
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


@pytest.mark.asyncio
async def test_organization_registration_starts_pending(client):
    organization, _ = await register_org(client, "registration")

    assert UUID(organization["organization_id"])
    assert organization["web_id"].startswith("ORG-")
    assert organization["status"] == "PENDING"
    assert organization["verification_status"] == "PENDING"


@pytest.mark.asyncio
async def test_duplicate_organization_email_is_rejected(client):
    email = unique_email("duplicate")
    password = "StrongPassword123!"

    payload = {
        "organization_email": email,
        "password": password,
        "organization_name": "Duplicate Test Organization",
        "organization_identifier": f"ID-{uuid4().hex[:12]}",
    }

    first = await client.post(
        "/api/v1/organizations/register",
        json=payload,
    )

    assert first.status_code == 201, first.text

    duplicate_payload = {
        **payload,
        "organization_name": "Duplicate Test Organization 2",
        "organization_identifier": f"ID-{uuid4().hex[:12]}",
    }

    second = await client.post(
        "/api/v1/organizations/register",
        json=duplicate_payload,
    )

    assert second.status_code == 409


@pytest.mark.asyncio
async def test_organization_admin_can_manage_own_department(client):
    organization, password = await register_org(
        client,
        "department",
    )

    auth = await login(
        client,
        organization["organization_email"],
        password,
    )

    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
    }

    organization_id = organization["organization_id"]

    create_response = await client.post(
        f"/api/v1/organizations/{organization_id}/departments",
        headers=headers,
        json={
            "name": "Engineering",
            "code": f"ENG-{uuid4().hex[:6]}",
        },
    )

    assert create_response.status_code == 201, create_response.text

    list_response = await client.get(
        f"/api/v1/organizations/{organization_id}/departments",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1


@pytest.mark.asyncio
async def test_organization_tenant_isolation(client):
    organization_a, password_a = await register_org(
        client,
        "tenant_a",
    )

    organization_b, password_b = await register_org(
        client,
        "tenant_b",
    )

    auth_a = await login(
        client,
        organization_a["organization_email"],
        password_a,
    )

    auth_b = await login(
        client,
        organization_b["organization_email"],
        password_b,
    )

    headers_a = {
        "Authorization": f"Bearer {auth_a['access_token']}",
    }

    headers_b = {
        "Authorization": f"Bearer {auth_b['access_token']}",
    }

    org_a = organization_a["organization_id"]
    org_b = organization_b["organization_id"]

    create_response = await client.post(
        f"/api/v1/organizations/{org_a}/departments",
        headers=headers_a,
        json={
            "name": "Private Department",
            "code": f"PRV-{uuid4().hex[:6]}",
        },
    )

    assert create_response.status_code == 201

    cross_org = await client.get(
        f"/api/v1/organizations/{org_a}/departments",
        headers=headers_b,
    )

    assert cross_org.status_code == 403

    own_org = await client.get(
        f"/api/v1/organizations/{org_b}/departments",
        headers=headers_b,
    )

    assert own_org.status_code == 200


@pytest.mark.asyncio
async def test_employee_creation_and_duplicate_id(client):
    organization, password = await register_org(
        client,
        "employee",
    )

    auth = await login(
        client,
        organization["organization_email"],
        password,
    )

    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
    }

    organization_id = organization["organization_id"]

    employee_id = f"EMP-{uuid4().hex[:8]}"

    first = await client.post(
        f"/api/v1/organizations/{organization_id}/employees",
        headers=headers,
        json={
            "employee_id": employee_id,
            "name": "Test Employee",
            "email": unique_email("employee"),
            "branch": "Head Office",
        },
    )

    assert first.status_code == 201, first.text

    second = await client.post(
        f"/api/v1/organizations/{organization_id}/employees",
        headers=headers,
        json={
            "employee_id": employee_id,
            "name": "Duplicate Employee",
            "email": unique_email("employee_duplicate"),
            "branch": "Head Office",
        },
    )

    assert second.status_code in {400, 409}


@pytest.mark.asyncio
async def test_employee_search_by_employee_id(client):
    organization, password = await register_org(
        client,
        "employee_search",
    )

    auth = await login(
        client,
        organization["organization_email"],
        password,
    )

    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
    }

    organization_id = organization["organization_id"]
    employee_id = f"SEARCH-{uuid4().hex[:8]}"

    create_response = await client.post(
        f"/api/v1/organizations/{organization_id}/employees",
        headers=headers,
        json={
            "employee_id": employee_id,
            "name": "Search Employee",
            "email": unique_email("search_employee"),
            "branch": "Head Office",
        },
    )

    assert create_response.status_code == 201

    search_response = await client.get(
        f"/api/v1/organizations/{organization_id}/employees/by-employee-id/{employee_id}",
        headers=headers,
    )

    assert search_response.status_code == 200
    assert search_response.json()["employee_id"] == employee_id


@pytest.mark.asyncio
async def test_invitation_creation_returns_token_and_stores_hash(client):
    organization, password = await register_org(
        client,
        "invitation",
    )

    auth = await login(
        client,
        organization["organization_email"],
        password,
    )

    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
    }

    organization_id = organization["organization_id"]

    employee = await client.post(
        f"/api/v1/organizations/{organization_id}/employees",
        headers=headers,
        json={
            "employee_id": f"INV-{uuid4().hex[:8]}",
            "name": "Invitation Employee",
            "email": unique_email("invited"),
            "branch": "Head Office",
        },
    )

    assert employee.status_code == 201, employee.text

    employee_uuid = employee.json()["id"]

    invitation = await client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        headers=headers,
        json={
            "employee_id": employee_uuid,
            "expires_in_hours": 72,
        },
    )

    assert invitation.status_code == 201, invitation.text

    data = invitation.json()

    assert data["token"]
    assert data["status"] == "PENDING"

    async with AsyncSessionLocal() as db:
        stored = await db.get(
            Invitation,
            UUID(data["id"]),
        )

        assert stored is not None
        assert stored.token_hash != data["token"]
        assert len(stored.token_hash) == 64


@pytest.mark.asyncio
async def test_invitation_is_single_use(client):
    organization, password = await register_org(
        client,
        "single_use",
    )

    auth = await login(
        client,
        organization["organization_email"],
        password,
    )

    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
    }

    organization_id = organization["organization_id"]

    employee = await client.post(
        f"/api/v1/organizations/{organization_id}/employees",
        headers=headers,
        json={
            "employee_id": f"ONE-{uuid4().hex[:8]}",
            "name": "Single Use Employee",
            "email": unique_email("single_use"),
            "branch": "Head Office",
        },
    )

    assert employee.status_code == 201

    invitation = await client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        headers=headers,
        json={
            "employee_id": employee.json()["id"],
            "expires_in_hours": 72,
        },
    )

    assert invitation.status_code == 201

    token = invitation.json()["token"]

    first = await client.post(
        f"/api/v1/organizations/{organization_id}/invitations/accept",
        json={"token": token},
    )

    assert first.status_code == 200
    assert first.json()["status"] == "ACCEPTED"

    second = await client.post(
        f"/api/v1/organizations/{organization_id}/invitations/accept",
        json={"token": token},
    )

    assert second.status_code == 400


@pytest.mark.asyncio
async def test_organization_role_is_created_correctly(client):
    organization, _ = await register_org(
        client,
        "role",
    )

    async with AsyncSessionLocal() as db:
        user = await db.scalar(
            select(User).where(
                User.email == organization["organization_email"]
            )
        )

        assert user is not None
        assert user.role_id is not None

        role = await db.scalar(
            select(Role).where(
                Role.id == user.role_id
            )
        )

        assert role is not None
        assert role.name == "ORGANIZATION_ADMIN"