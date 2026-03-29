import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from app.models.user import UserRole

# --- FIXTURES ---


@pytest.fixture
async def sample_store(client_fixture: AsyncClient, owner_token):
    payload = {
        "name": "Booking Test Store",
        "address": "Book St",
        "contact_number": "555-0312",
    }
    resp = await client_fixture.post(
        "/api/v1/owner/stores/",
        json=payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    store = resp.json()

    # Add service
    await client_fixture.post(
        f"/api/v1/owner/stores/{store['id']}/services",
        json={"name": "Haircut", "price": 500.0, "duration_minutes": 30},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    # Add hours
    for i in range(7):
        await client_fixture.post(
            f"/api/v1/owner/stores/{store['id']}/store-hours",
            json={"day_of_week": i, "open_time": "09:00:00", "close_time": "21:00:00"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )

    # Re-fetch with details
    resp = await client_fixture.get(f"/api/v1/users/stores/{store['id']}")
    return resp.json()


# --- TESTS ---


@pytest.mark.asyncio
async def test_auth_booking_links_to_user(
    client_fixture: AsyncClient, user_token, sample_store
):
    # Book tomorrow
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_store["services"][0]["id"],
        "customer_name": "User A Actual Name",
        "start_time": start_time.isoformat(),
    }

    # 1. POST as User A
    resp = await client_fixture.post(
        "/api/v1/users/bookings/",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 201
    booking_id = resp.json()["id"]

    # 2. Check my bookings list
    list_resp = await client_fixture.get(
        "/api/v1/users/bookings/", headers={"Authorization": f"Bearer {user_token}"}
    )

    assert list_resp.status_code == 200
    assert any(b["id"] == booking_id for b in list_resp.json())

    # 3. Verify store info is nested
    assert list_resp.json()[0]["store"]["name"] == sample_store["name"]


@pytest.mark.asyncio
async def test_user_cannot_see_others_bookings(
    client_fixture: AsyncClient, user_token, sample_store
):
    # Second User
    import asyncio

    email2 = f"other_{asyncio.get_event_loop().time()}@saloon.com"
    await client_fixture.post(
        "/api/v1/auth/register",
        json={
            "email": email2,
            "full_name": "Other User",
            "password": "password",
            "role": UserRole.CUSTOMER,
        },
    )
    resp2 = await client_fixture.post(
        "/api/v1/auth/login", data={"username": email2, "password": "password"}
    )
    user_token_b = resp2.json()["access_token"]

    # User A creates a booking

    start_time = datetime.now(timezone.utc) + timedelta(days=2)
    await client_fixture.post(
        "/api/v1/users/bookings/",
        json={
            "store_id": sample_store["id"],
            "service_id": sample_store["services"][0]["id"],
            "customer_name": "User A",
            "start_time": start_time.isoformat(),
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # User B checks their bookings
    list_resp = await client_fixture.get(
        "/api/v1/users/bookings/", headers={"Authorization": f"Bearer {user_token_b}"}
    )
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_anon_booking_allowed_but_not_listed(
    client_fixture: AsyncClient, sample_store, user_token
):
    # 1. Anonymous booking
    start_time = datetime.now(timezone.utc) + timedelta(days=3)
    resp = await client_fixture.post(
        "/api/v1/users/bookings/",
        json={
            "store_id": sample_store["id"],
            "service_id": sample_store["services"][0]["id"],
            "customer_name": "Anonymous Joe",
            "start_time": start_time.isoformat(),
        },
    )
    assert resp.status_code == 201

    # 2. Listing for User A remains empty (unless they had others)
    list_resp = await client_fixture.get(
        "/api/v1/users/bookings/", headers={"Authorization": f"Bearer {user_token}"}
    )

    assert not any(b["customer_name"] == "Anonymous Joe" for b in list_resp.json())
