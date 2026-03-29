import pytest
from httpx import AsyncClient
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_register_customer(client_fixture: AsyncClient):
    payload = {
        "email": "customer@example.com",
        "full_name": "Test Customer",
        "password": "strongpassword123",
        "role": UserRole.CUSTOMER,
    }
    resp = await client_fixture.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    assert resp.json()["email"] == payload["email"]
    assert "password" not in resp.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client_fixture: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "First User",
        "password": "password",
        "role": UserRole.CUSTOMER,
    }
    await client_fixture.post("/api/v1/auth/register", json=payload)

    # Try again
    resp = await client_fixture.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400
    assert "exists" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_and_me(client_fixture: AsyncClient):
    # 1. Register
    email = "login@example.com"
    password = "secretpassword"
    await client_fixture.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Login User",
            "password": password,
            "role": UserRole.CUSTOMER,
        },
    )

    # 2. Login
    login_resp = await client_fixture.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},  # OAuth2 form data
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token

    # 3. Access /me
    me_resp = await client_fixture.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email


@pytest.mark.asyncio
async def test_invalid_login(client_fixture: AsyncClient):
    resp = await client_fixture.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
