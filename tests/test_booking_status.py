import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

# --- FIXTURES ---


@pytest.fixture
async def sample_store(client_fixture: AsyncClient, owner_token):
    payload = {
        "name": "Status Test Store",
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


@pytest.fixture
async def sample_hours(client_fixture: AsyncClient, sample_store, owner_token):
    for day in range(7):
        payload = {
            "day_of_week": day,
            "open_time": "09:00:00",
            "close_time": "21:00:00",
        }
        await client_fixture.post(
            f"/api/v1/owner/stores/{sample_store['id']}/store-hours",
            json=payload,
            headers={"Authorization": f"Bearer {owner_token}"},
        )


@pytest.fixture
async def sample_service(client_fixture: AsyncClient, sample_store, owner_token):
    payload = {"name": "Status Service", "price": 100.0, "duration_minutes": 30}
    resp = await client_fixture.post(
        f"/api/v1/owner/stores/{sample_store['id']}/services",
        json=payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    return resp.json()


@pytest.fixture
async def active_booking(
    client_fixture: AsyncClient, sample_store, sample_service, sample_hours
):
    # Book for 5 hours from now
    start_time = datetime.now(timezone.utc) + timedelta(hours=5)
    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Test User",
        "start_time": start_time.isoformat(),
    }
    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)
    return resp.json()


# --- OWNER STATUS TESTS ---


@pytest.mark.asyncio
async def test_owner_can_confirm_pending(
    client_fixture: AsyncClient, active_booking, owner_token
):
    # Move Pending -> Confirmed
    resp = await client_fixture.patch(
        f"/api/v1/owner/bookings/{active_booking['id']}/status",
        json={"status": "confirmed"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_owner_can_complete_confirmed(
    client_fixture: AsyncClient, active_booking, owner_token
):
    # First Confirm
    await client_fixture.patch(
        f"/api/v1/owner/bookings/{active_booking['id']}/status",
        json={"status": "confirmed"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Then Complete
    resp = await client_fixture.patch(
        f"/api/v1/owner/bookings/{active_booking['id']}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_terminal_state_locked(
    client_fixture: AsyncClient, active_booking, owner_token
):
    # 1. Cancel the booking (Terminal)
    await client_fixture.patch(
        f"/api/v1/owner/bookings/{active_booking['id']}/status",
        json={"status": "cancelled"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # 2. Try to mark as confirmed (Should Fail)
    resp = await client_fixture.patch(
        f"/api/v1/owner/bookings/{active_booking['id']}/status",
        json={"status": "confirmed"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    assert resp.status_code == 400
    assert "terminal state" in resp.json()["detail"].lower()


# --- CANCELLATION POLICY TESTS ---


@pytest.mark.asyncio
async def test_user_can_cancel_outside_2hr_window(
    client_fixture: AsyncClient, active_booking
):
    # active_booking is set for 5 hours from now
    resp = await client_fixture.patch(
        f"/api/v1/users/bookings/{active_booking['id']}/cancel"
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_user_cannot_cancel_inside_2hr_window(
    client_fixture: AsyncClient, sample_store, sample_service, sample_hours
):
    # Book for 30 minutes from now
    start_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Laggard User",
        "start_time": start_time.isoformat(),
    }
    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)
    booking = resp.json()

    # Try to cancel
    resp = await client_fixture.patch(f"/api/v1/users/bookings/{booking['id']}/cancel")
    assert resp.status_code == 400
    assert "within 2 hours" in resp.json()["detail"].lower()


# --- AVAILABILITY RECOVERY TEST ---


@pytest.mark.asyncio
async def test_cancellation_release_slots(
    client_fixture: AsyncClient, sample_store, sample_hours, sample_service
):
    # 1. Book a slot for tomorrow
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    target_date = tomorrow.strftime("%Y-%m-%d")
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

    payload = {
        "store_id": sample_store["id"],
        "service_id": sample_service["id"],
        "customer_name": "Slot Blocker",
        "start_time": start_time.isoformat(),
    }
    resp = await client_fixture.post("/api/v1/users/bookings/", json=payload)
    booking = resp.json()

    # 2. Verify slot 10:00 is missing from discovery
    resp = await client_fixture.get(
        f"/api/v1/users/bookings/store/{sample_store['id']}/slots",
        params={"service_id": sample_service["id"], "target_date": target_date},
    )
    slots_before = [s["start_time"] for s in resp.json()]
    expected_1000 = start_time.isoformat().replace("+00:00", "Z")
    assert expected_1000 not in slots_before

    # 3. Cancel the booking
    await client_fixture.patch(f"/api/v1/users/bookings/{booking['id']}/cancel")

    # 4. Verify slot 10:00 is RE-ENABLED
    resp = await client_fixture.get(
        f"/api/v1/users/bookings/store/{sample_store['id']}/slots",
        params={"service_id": sample_service["id"], "target_date": target_date},
    )
    slots_after = [s["start_time"] for s in resp.json()]
    assert expected_1000 in slots_after
