import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

# --- FIXTURES FOR ISOLATION ---


@pytest.fixture
async def sample_store(client_fixture: AsyncClient, owner_token):
    payload = {
        "name": "Test Store",
        "address": "Kochi",
        "contact_number": "123",
        "latitude": 10.0,
        "longitude": 76.0,
    }
    resp = await client_fixture.post(
        "/api/v1/owner/stores/",
        json=payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    return resp.json()


@pytest.fixture
async def sample_hours(client_fixture: AsyncClient, sample_store, owner_token):
    """Sets 9 AM - 8 PM hours for every day of the week to ensure test stability."""
    created_hours = []
    for day in range(7):
        payload = {
            "day_of_week": day,
            "open_time": "09:00:00",
            "close_time": "20:00:00",
        }
        resp = await client_fixture.post(
            f"/api/v1/owner/stores/{sample_store['id']}/store-hours",
            json=payload,
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        created_hours.append(resp.json())
    return created_hours


@pytest.fixture
async def sample_service(client_fixture: AsyncClient, sample_store, owner_token):
    payload = {"name": "Haircut", "price": 500.0, "duration_minutes": 30}
    resp = await client_fixture.post(
        f"/api/v1/owner/stores/{sample_store['id']}/services",
        json=payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    return resp.json()


# --- CONFLICT ENGINE TESTS ---


@pytest.mark.asyncio
async def test_create_booking_success(
    client_fixture: AsyncClient, sample_store, sample_hours, sample_service
):
    """Test #1: Standard successful booking path."""
    # Book for tomorrow at 12:00 PM
    start_time = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )

    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Alice",
        "start_time": start_time.isoformat(),
    }

    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)
    assert resp.status_code == 201

    data = resp.json()
    actual_end = datetime.fromisoformat(data["end_time"]).replace(tzinfo=timezone.utc)
    expected_end = start_time + timedelta(minutes=sample_service["duration_minutes"])
    assert actual_end == expected_end


@pytest.mark.asyncio
async def test_prevent_double_booking(
    client_fixture: AsyncClient, sample_store, sample_hours, sample_service
):
    """Test #2: Block two users from booking the exact same slot."""
    start_time = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=14, minute=0, second=0, microsecond=0
    )

    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "User 1",
        "start_time": start_time.isoformat(),
    }

    # First booking succeeds
    await client_fixture.post("/api/v1/users/bookings/", json=payload)

    # Second booking at same time fails
    payload["customer_name"] = "User 2"
    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)

    assert resp.status_code == 400
    assert "already booked" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prevent_booking_outside_hours(
    client_fixture: AsyncClient, sample_store, sample_hours, sample_service
):
    """Test #3: Block booking if time falls outside 09:00 - 20:00."""
    # Try to book at 11:00 PM (23:00)
    start_time = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=23, minute=0, second=0, microsecond=0
    )

    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Night Owl",
        "start_time": start_time.isoformat(),
    }

    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)
    assert resp.status_code == 400
    assert "outside operating hours" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prevent_booking_on_unconfigured_day(
    client_fixture: AsyncClient, sample_store, sample_service
):
    """Test #4: Block booking if the owner hasn't set hours for that day yet."""
    # Note: We do NOT use the 'sample_hours' fixture here to simulate a fresh store
    start_time = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Early Bird",
        "start_time": start_time.isoformat(),
    }

    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)
    assert resp.status_code == 400
    assert "not configured" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_booking_slots_discovery(
    client_fixture: AsyncClient, sample_store, sample_hours, sample_service
):
    """Test #5: Verify available slots generation and overlap filtering."""

    # 1. Target exactly tomorrow
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    target_date_str = tomorrow.strftime("%Y-%m-%d")

    # Book a single 30m slot at 10:00 (10:00 -> 10:30)
    booking_start = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Blocker User",
        "start_time": booking_start.isoformat(),
    }
    await client_fixture.post("/api/v1/users/bookings/", json=payload)

    # 2. Fetch Slots
    url = f"/api/v1/users/bookings/store/{sample_store['id']}/slots"
    params = {"service_id": sample_service["id"], "target_date": target_date_str}
    resp = await client_fixture.get(url, params=params)

    assert resp.status_code == 200
    slots = resp.json()

    # We expect hours from 09:00 to 20:00 (11 hours) -> 22 possible 30m slots.
    # Minus 1 blocked slot (10:00) -> 21
    assert len(slots) == 21

    # Check that 09:30 exists, but 10:00 does NOT
    start_times = [s["start_time"] for s in slots]

    expected_930 = (
        tomorrow.replace(hour=9, minute=30, second=0, microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    expected_1000 = booking_start.isoformat().replace("+00:00", "Z")

    assert expected_930 in start_times
    assert expected_1000 not in start_times

    # Verify the last valid slot ends AT closing time.
    # Open 0900 -> Close 2000. Service=30m. Last possible slot should start at 19:30.
    last_slot_expected = (
        tomorrow.replace(hour=19, minute=30, second=0, microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    assert start_times[-1] == last_slot_expected
