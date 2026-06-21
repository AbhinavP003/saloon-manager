"""Production smoke test for beta checklist (API flows)."""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import httpx

API_BASE = os.environ.get(
    "API_BASE_URL", "https://saloon-backend-lj4j5kxljq-el.a.run.app"
).rstrip("/")
API_V1 = f"{API_BASE}/api/v1"
FRONTEND = os.environ.get(
    "FRONTEND_URL", "https://saloon-frontend-lj4j5kxljq-el.a.run.app"
).rstrip("/")


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        health = await client.get(f"{API_BASE}/health")
        if health.status_code != 200 or health.json().get("status") != "ok":
            fail(f"/health -> {health.status_code}")
        ok("/health")

        stores = await client.get(
            f"{API_V1}/users/stores/",
            headers={"Origin": FRONTEND},
        )
        if stores.status_code != 200:
            fail(f"stores list -> {stores.status_code}")
        cors = stores.headers.get("access-control-allow-origin", "")
        if FRONTEND not in cors and cors != "*":
            fail(f"CORS header missing frontend origin (got {cors!r})")
        ok("stores list + CORS")

        data = stores.json()
        if not data:
            fail("stores list empty (run populate_preview.py)")
        store = data[0]
        store_id = store["id"]
        service = store["services"][0]
        ok(f"discovery: store {store['name']}")

        reg_email = f"e2e-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}@test.com"
        reg = await client.post(
            f"{API_V1}/auth/register",
            json={
                "email": reg_email,
                "password": "password123",
                "full_name": "E2E User",
                "role": "customer",
            },
        )
        if reg.status_code not in (200, 201):
            fail(f"register -> {reg.status_code} {reg.text}")
        ok("register customer")

        login = await client.post(
            f"{API_V1}/auth/login",
            data={"username": reg_email, "password": "password123"},
        )
        if login.status_code != 200:
            fail(f"login -> {login.status_code}")
        token = login.json()["access_token"]
        ok("login customer")

        tomorrow = (datetime.now(timezone.utc) + timedelta(days=2)).date().isoformat()
        slots = await client.get(
            f"{API_V1}/users/bookings/store/{store_id}/slots",
            params={"service_id": service["id"], "target_date": tomorrow},
        )
        if slots.status_code != 200:
            fail(f"slots -> {slots.status_code} {slots.text}")
        slot_list = slots.json()
        if not slot_list:
            fail("no slots returned")
        start_time = slot_list[0]["start_time"]
        ok("browse slots")

        book = await client.post(
            f"{API_V1}/users/bookings/",
            json={
                "store_id": store_id,
                "service_id": service["id"],
                "customer_name": "E2E User",
                "start_time": start_time,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if book.status_code not in (200, 201):
            fail(f"book -> {book.status_code} {book.text}")
        booking_id = book.json()["id"]
        ok(f"book -> {booking_id}")

        owner_login = await client.post(
            f"{API_V1}/auth/login",
            data={"username": "owner@saloon.com", "password": "password"},
        )
        if owner_login.status_code != 200:
            fail(f"owner login -> {owner_login.status_code}")
        owner_token = owner_login.json()["access_token"]
        ok("owner login")

        confirm = await client.patch(
            f"{API_V1}/owner/bookings/{booking_id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        if confirm.status_code != 200:
            fail(f"confirm -> {confirm.status_code} {confirm.text}")
        ok("owner confirm")

        complete = await client.patch(
            f"{API_V1}/owner/bookings/{booking_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        if complete.status_code != 200:
            fail(f"complete -> {complete.status_code} {complete.text}")
        ok("owner complete")

        fe = await client.get(FRONTEND)
        if fe.status_code != 200:
            fail(f"frontend home -> {fe.status_code}")
        ok("frontend home loads")

        if "localhost:8000" in fe.text:
            fail("frontend HTML references localhost:8000")

        print("\n--- ALL API SMOKE CHECKS PASSED ---")


if __name__ == "__main__":
    asyncio.run(main())
