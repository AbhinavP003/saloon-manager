import httpx
import asyncio
from datetime import datetime, timedelta, timezone


async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000/api/v1") as client:
        print("--- POPULATING PREVIEW DATA ---")

        # 1. Owner Setup
        email = "owner@saloon.com"
        await client.post(
            "/auth/register",
            json={
                "email": email,
                "full_name": "Premium Owner",
                "password": "password",
                "role": "owner",
            },
        )
        resp = await client.post(
            "/auth/login", data={"username": email, "password": "password"}
        )
        owner_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {owner_token}"}

        # 2. Create Store
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
        store = resp.json()
        sid = store["id"]
        print(f"STORE CREATED: {sid}")

        # 3. Create Services
        await client.post(
            f"/owner/stores/{sid}/services",
            json={
                "name": "Luxury Haircut",
                "price": 500,
                "duration_minutes": 30,
                "description": "Master stylist precision cut.",
            },
            headers=headers,
        )
        resp = await client.post(
            f"/owner/stores/{sid}/services",
            json={
                "name": "Spa Treatment",
                "price": 1200,
                "duration_minutes": 60,
                "description": "Full face and scalp ritual.",
            },
            headers=headers,
        )
        svc_spa = resp.json()
        svc_hair = (
            store["services"][0]
            if "services" in store and store["services"]
            else svc_spa
        )
        sid_hair = svc_hair["id"] if isinstance(svc_hair, dict) else svc_hair.id

        # 4. Create Hours
        for i in range(7):
            await client.post(
                f"/owner/stores/{sid}/store-hours",
                json={
                    "day_of_week": i,
                    "open_time": "09:00:00",
                    "close_time": "21:00:00",
                },
                headers=headers,
            )

        # 5. Create Bookings
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

        # Pending Booking (Alice)
        await client.post(
            "/users/bookings/",
            json={
                "store_id": sid,
                "service_id": sid_hair,
                "customer_name": "Alice",
                "start_time": tomorrow.replace(hour=10, minute=0, second=0).isoformat(),
            },
        )

        # Confirmed Booking (Bob)
        resp = await client.post(
            "/users/bookings/",
            json={
                "store_id": sid,
                "service_id": svc_spa["id"],
                "customer_name": "Bob",
                "start_time": tomorrow.replace(hour=14, minute=0, second=0).isoformat(),
            },
        )
        booking_bob = resp.json()
        await client.patch(
            f"/owner/bookings/{booking_bob['id']}/status",
            json={"status": "confirmed"},
            headers=headers,
        )

        # 6. Customer Setup
        await client.post(
            "/auth/register",
            json={
                "email": "customer@test.com",
                "full_name": "Frequent Flyer",
                "password": "password",
                "role": "customer",
            },
        )

        print("--- COMPLETE ---")


if __name__ == "__main__":
    asyncio.run(main())
