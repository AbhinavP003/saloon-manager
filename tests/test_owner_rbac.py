import pytest
from httpx import AsyncClient
from app.models.user import UserRole

# --- FIXTURES ---


@pytest.fixture
async def owner_token(client_fixture: AsyncClient):
    email = "owner@saloon.com"
    password = "password"
    await client_fixture.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Saloon Owner",
            "password": password,
            "role": UserRole.STORE_OWNER,
        },
    )
    resp = await client_fixture.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    return resp.json()["access_token"]


@pytest.fixture
async def admin_token(client_fixture: AsyncClient):
    email = "admin@saloon.com"
    password = "password"
    await client_fixture.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "System Admin",
            "password": password,
            "role": UserRole.ADMIN,
        },
    )
    resp = await client_fixture.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    return resp.json()["access_token"]


@pytest.fixture
async def user_token(client_fixture: AsyncClient):
    email = "user@saloon.com"
    password = "password"
    await client_fixture.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Standard User",
            "password": password,
            "role": UserRole.CUSTOMER,
        },
    )
    resp = await client_fixture.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    return resp.json()["access_token"]


@pytest.fixture
async def sample_store(client_fixture: AsyncClient, owner_token):
    payload = {
        "name": "RBAC Tested Store",
        "address": "Test Ave",
        "contact_number": "555",
        "latitude": 10.0,
        "longitude": 76.0,
    }
    resp = await client_fixture.post(
        "/api/v1/owner/stores/",
        json=payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    return resp.json()


# --- TESTS ---


@pytest.mark.asyncio
async def test_owner_can_create_store(client_fixture: AsyncClient, owner_token):
    payload = {
        "name": "My Saloon",
        "address": "123 Main St",
        "contact_number": "555-0199",
        "latitude": 10.0,
        "longitude": 76.0,
    }
    resp = await client_fixture.post(
        "/api/v1/owner/stores/",
        json=payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Saloon"


@pytest.mark.asyncio
async def test_user_cannot_create_store(client_fixture: AsyncClient, user_token):
    payload = {
        "name": "Hack Saloon",
        "address": "Void",
        "contact_number": "000",
    }
    resp = await client_fixture.post(
        "/api/v1/owner/stores/",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_owner_cannot_add_service_to_other_store(
    client_fixture: AsyncClient, owner_token, sample_store
):
    # Register a DIFFERENT owner
    email2 = "owner2@saloon.com"
    await client_fixture.post(
        "/api/v1/auth/register",
        json={
            "email": email2,
            "full_name": "Saloon Owner 2",
            "password": "password",
            "role": UserRole.STORE_OWNER,
        },
    )
    resp2 = await client_fixture.post(
        "/api/v1/auth/login", data={"username": email2, "password": "password"}
    )
    token2 = resp2.json()["access_token"]

    # Try to add service to store owned by first owner
    payload = {"name": "Unauthorized Shave", "price": 50.0, "duration_minutes": 20}
    resp = await client_fixture.post(
        f"/api/v1/owner/stores/{sample_store['id']}/services",
        json=payload,
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_can_manage_any_store(
    client_fixture: AsyncClient, admin_token, sample_store
):
    payload = {"name": "Admin Forced Service", "price": 10.0, "duration_minutes": 10}

    resp = await client_fixture.post(
        f"/api/v1/owner/stores/{sample_store['id']}/services",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Admin Forced Service"
