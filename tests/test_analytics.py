"""Tests for owner store analytics endpoint."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def store_with_service(client_fixture: AsyncClient, owner_token):
    store_resp = await client_fixture.post(
        "/api/v1/owner/stores/",
        json={
            "name": "Analytics Salon",
            "address": "Analytics Ave",
            "contact_number": "555",
            "latitude": 10.0,
            "longitude": 76.0,
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    store = store_resp.json()

    for day in range(7):
        await client_fixture.post(
            f"/api/v1/owner/stores/{store['id']}/store-hours",
            json={
                "day_of_week": day,
                "open_time": "09:00:00",
                "close_time": "20:00:00",
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )

    service_resp = await client_fixture.post(
        f"/api/v1/owner/stores/{store['id']}/services",
        json={
            "name": "Haircut",
            "price": 500.0,
            "duration_minutes": 30,
            "description": "Standard cut",
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    service = service_resp.json()
    return store, service


@pytest.mark.asyncio
async def test_owner_can_fetch_monthly_analytics(
    client_fixture: AsyncClient, owner_token, store_with_service
):
    store, service = store_with_service
    month = "2026-06-01T10:00:00+00:00"

    booking_resp = await client_fixture.post(
        "/api/v1/users/bookings/",
        json={
            "store_id": store["id"],
            "service_id": service["id"],
            "customer_name": "Analytics Customer",
            "start_time": month,
        },
    )
    booking = booking_resp.json()

    await client_fixture.patch(
        f"/api/v1/owner/bookings/{booking['id']}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    resp = await client_fixture.get(
        f"/api/v1/owner/stores/{store['id']}/analytics?month=2026-06",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["completed_bookings"] == 1
    assert float(data["monthly_revenue"]) == 500.0
    assert len(data["busy_hours"]) == 1
    assert data["busy_hours"][0]["hour"] == 10


@pytest.mark.asyncio
async def test_customer_cannot_fetch_analytics(
    client_fixture: AsyncClient, user_token, store_with_service
):
    store, _ = store_with_service
    resp = await client_fixture.get(
        f"/api/v1/owner/stores/{store['id']}/analytics?month=2026-06",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403
