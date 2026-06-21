import asyncio
import os
from datetime import datetime, timedelta, timezone

import httpx

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_V1 = f"{API_BASE}/api/v1"


async def register_or_login(client: httpx.AsyncClient, email: str, password: str, **register_extra):
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": password, **register_extra},
    )
    if resp.status_code not in (200, 201, 409):
        resp.raise_for_status()
    login = await client.post("/auth/login", data={"username": email, "password": password})
    login.raise_for_status()
    return login.json()["access_token"]


async def main():
    async with httpx.AsyncClient(base_url=API_V1, timeout=30.0) as client:
        print(f"--- POPULATING PREVIEW DATA ({API_BASE}) ---")

        owner_token = await register_or_login(
            client,
            "owner@saloon.com",
            "password",
            full_name="Premium Owner",
            role="owner",
        )
        headers = {"Authorization": f"Bearer {owner_token}"}

        resp = await client.post(
            "/owner/stores/",
            json={
                "name": "The Grand Saloon",
                "address": "123 Elegance Lane, Kochi",
                "contact_number": "555-0101",
                "latitude": 9.9312,
                "longitude": 76.2673,
            },
            headers=headers,
        )
        resp.raise_for_status()
        store = resp.json()
        sid = store["id"]
        print(f"STORE CREATED: {sid}")

        hair = await client.post(
            f"/owner/stores/{sid}/services",
            json={
                "name": "Luxury Haircut",
                "price": 500,
                "duration_minutes": 30,
                "description": "Master stylist precision cut.",
            },
            headers=headers,
        )
        hair.raise_for_status()
        sid_hair = hair.json()["id"]

        spa = await client.post(
            f"/owner/stores/{sid}/services",
            json={
                "name": "Spa Treatment",
                "price": 1200,
                "duration_minutes": 60,
                "description": "Full face and scalp ritual.",
            },
            headers=headers,
        )
        spa.raise_for_status()
        svc_spa = spa.json()

        for i in range(7):
            hours = await client.post(
                f"/owner/stores/{sid}/store-hours",
                json={
                    "day_of_week": i,
                    "open_time": "09:00:00",
                    "close_time": "21:00:00",
                },
                headers=headers,
            )
            hours.raise_for_status()

        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

        await client.post(
            "/users/bookings/",
            json={
                "store_id": sid,
                "service_id": sid_hair,
                "customer_name": "Alice",
                "start_time": tomorrow.replace(hour=10, minute=0, second=0).isoformat(),
            },
        )

        bob = await client.post(
            "/users/bookings/",
            json={
                "store_id": sid,
                "service_id": svc_spa["id"],
                "customer_name": "Bob",
                "start_time": tomorrow.replace(hour=14, minute=0, second=0).isoformat(),
            },
        )
        bob.raise_for_status()
        booking_bob = bob.json()
        confirm = await client.patch(
            f"/owner/bookings/{booking_bob['id']}/status",
            json={"status": "confirmed"},
            headers=headers,
        )
        confirm.raise_for_status()

        await register_or_login(
            client,
            "customer@test.com",
            "password",
            full_name="Frequent Flyer",
            role="customer",
        )

        print("--- COMPLETE ---")


if __name__ == "__main__":
    asyncio.run(main())
