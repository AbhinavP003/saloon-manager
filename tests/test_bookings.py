import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_booking_flow(client_fixture: AsyncClient):
    """
    Dynamic ID Flow:
    1. [Owner] Create a Store
    2. [Owner] Set Operating Hours
    3. [Owner] Create a Service
    4. [User]  Book that Service
    """

    # 1. [OWNER] CREATE DYNAMIC STORE
    store_payload = {
        "name": "Test Dynamic Saloon",
        "address": "Kochi",
        "contact_number": "9876543210",
        "latitude": 10.01,
        "longitude": 76.34,
    }
    # Hits the Owner endpoint
    store_resp = await client_fixture.post("/api/v1/owner/stores/", json=store_payload)
    assert store_resp.status_code == 201
    store_id = store_resp.json()["id"]

    # 1.5 [OWNER] SET OPERATING HOURS
    booking_date = datetime.now(timezone.utc) + timedelta(days=2)
    target_weekday = booking_date.weekday()

    hours_payload = {
        "day_of_week": target_weekday,
        "open_time": "09:00:00",
        "close_time": "20:00:00",
    }

    # Hits the Owner endpoint
    hours_resp = await client_fixture.post(
        f"/api/v1/owner/stores/{store_id}/store-hours", json=hours_payload
    )
    assert hours_resp.status_code == 201, f"Hours setup failed: {hours_resp.text}"

    # 2. [OWNER] CREATE DYNAMIC SERVICE
    service_payload = {
        "name": "Dynamic Haircut",
        "description": "Test Service",
        "price": 500.0,
        "duration_minutes": 30,
    }
    # Hits the Owner endpoint
    service_resp = await client_fixture.post(
        f"/api/v1/owner/stores/{store_id}/services", json=service_payload
    )
    assert service_resp.status_code == 201
    service_id = service_resp.json()["id"]

    # 3. [USER] ATTEMPT VALID BOOKING
    # Ensure it's the same day we set the hours for
    start_time = booking_date.replace(hour=10, minute=0, second=0, microsecond=0)

    booking_payload = {
        "store_id": store_id,
        "service_id": service_id,
        "customer_name": "Dynamic Alice",
        "start_time": start_time.isoformat(),
    }

    # Hits the User endpoint
    booking_resp = await client_fixture.post(
        "/api/v1/users/bookings/", json=booking_payload
    )

    # ASSERTIONS
    assert booking_resp.status_code == 201, f"Booking failed: {booking_resp.text}"
    data = booking_resp.json()
    assert data["store_id"] == store_id
    assert data["service_id"] == service_id

    # Verify calculated end_time (30 mins later)
    # Note: Using 'Z' to match the likely Pydantic/ISO output format
    actual_end = datetime.fromisoformat(data["end_time"]).replace(tzinfo=timezone.utc)
    # 2. Ensure your expected calculation is also UTC aware
    expected_end = (start_time + timedelta(minutes=30)).replace(tzinfo=timezone.utc)

    assert actual_end == expected_end
