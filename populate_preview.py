import asyncio
import os
from datetime import datetime, timedelta, timezone

import httpx

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_V1 = f"{API_BASE}/api/v1"

SEED_STORES = [
    {
        "name": "The Grand Saloon",
        "address": "123 Marine Drive, Kochi",
        "contact_number": "555-0101",
        "latitude": 9.9312,
        "longitude": 76.2673,
    },
    {
        "name": "Luxe Cuts Studio",
        "address": "45 MG Road, Ernakulam",
        "contact_number": "555-0102",
        "latitude": 9.9816,
        "longitude": 76.2837,
    },
    {
        "name": "Fort Kochi Grooming",
        "address": "12 Princess Street, Fort Kochi",
        "contact_number": "555-0103",
        "latitude": 9.9650,
        "longitude": 76.2424,
    },
    {
        "name": "Kakkanad Style House",
        "address": "88 Seaport-Airport Road, Kakkanad",
        "contact_number": "555-0104",
        "latitude": 10.0159,
        "longitude": 76.3419,
    },
    {
        "name": "Calicut Classic Barbers",
        "address": "22 SM Street, Kozhikode",
        "contact_number": "555-0105",
        "latitude": 11.2588,
        "longitude": 75.7804,
    },
    {
        "name": "Trivandrum Trim Lounge",
        "address": "9 Statue Junction, Thiruvananthapuram",
        "contact_number": "555-0106",
        "latitude": 8.5241,
        "longitude": 76.9366,
    },
    {
        "name": "Thrissur Royal Salon",
        "address": "34 Swaraj Round, Thrissur",
        "contact_number": "555-0107",
        "latitude": 10.5276,
        "longitude": 76.2144,
    },
    {
        "name": "Kottayam Gentleman's Club",
        "address": "7 Baker Junction, Kottayam",
        "contact_number": "555-0108",
        "latitude": 9.5916,
        "longitude": 76.5222,
    },
    {
        "name": "Alleppey Beach Cuts",
        "address": "3 Beach Road, Alappuzha",
        "contact_number": "555-0109",
        "latitude": 9.4981,
        "longitude": 76.3388,
    },
    {
        "name": "Palakkad Heritage Salon",
        "address": "19 Sultanpet, Palakkad",
        "contact_number": "555-0110",
        "latitude": 10.7867,
        "longitude": 76.6548,
    },
]

DEFAULT_SERVICES = [
    {
        "name": "Signature Haircut",
        "price": 450,
        "duration_minutes": 30,
        "description": "Precision cut with wash and style.",
    },
    {
        "name": "Beard Trim & Shape",
        "price": 250,
        "duration_minutes": 20,
        "description": "Hot towel, trim, and line-up.",
    },
    {
        "name": "Relaxing Head Spa",
        "price": 900,
        "duration_minutes": 45,
        "description": "Scalp massage and deep conditioning.",
    },
]


async def register_or_login(
    client: httpx.AsyncClient, email: str, password: str, **register_extra
):
    login = await client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    if login.status_code == 200:
        return login.json()["access_token"]

    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": password, **register_extra},
    )
    if resp.status_code not in (200, 201):
        resp.raise_for_status()
    login = await client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    login.raise_for_status()
    return login.json()["access_token"]


async def existing_store_names(client: httpx.AsyncClient) -> set[str]:
    resp = await client.get("/users/stores/")
    resp.raise_for_status()
    return {s["name"] for s in resp.json()}


async def create_store_hours(client: httpx.AsyncClient, store_id: str, headers: dict):
    for day in range(7):
        resp = await client.post(
            f"/owner/stores/{store_id}/store-hours",
            json={
                "day_of_week": day,
                "open_time": "09:00:00",
                "close_time": "21:00:00",
            },
            headers=headers,
        )
        resp.raise_for_status()


async def create_services(
    client: httpx.AsyncClient, store_id: str, headers: dict, store_index: int
) -> list[dict]:
    # Rotate which services each store offers for variety.
    picks = [
        DEFAULT_SERVICES[store_index % 3],
        DEFAULT_SERVICES[(store_index + 1) % 3],
    ]
    created = []
    for svc in picks:
        resp = await client.post(
            f"/owner/stores/{store_id}/services",
            json=svc,
            headers=headers,
        )
        resp.raise_for_status()
        created.append(resp.json())
    return created


async def seed_store(
    client: httpx.AsyncClient,
    store_data: dict,
    headers: dict,
    store_index: int,
) -> str | None:
    resp = await client.post("/owner/stores/", json=store_data, headers=headers)
    resp.raise_for_status()
    store = resp.json()
    store_id = store["id"]
    print(f"STORE CREATED: {store['name']} ({store_id})")

    await create_services(client, store_id, headers, store_index)
    await create_store_hours(client, store_id, headers)
    return store_id


async def main():
    async with httpx.AsyncClient(base_url=API_V1, timeout=60.0) as client:
        print(f"--- POPULATING PREVIEW DATA ({API_BASE}) ---")

        owner_token = await register_or_login(
            client,
            "owner@saloon.com",
            "password",
            full_name="Premium Owner",
            role="owner",
        )
        headers = {"Authorization": f"Bearer {owner_token}"}

        already = await existing_store_names(client)
        created_ids: list[str] = []

        for i, store_data in enumerate(SEED_STORES):
            if store_data["name"] in already:
                print(f"SKIP (exists): {store_data['name']}")
                continue
            store_id = await seed_store(client, store_data, headers, i)
            if store_id:
                created_ids.append(store_id)

        # Sample bookings on the first newly created store (or first seed store if all exist).
        if created_ids:
            first_id = created_ids[0]
            services_resp = await client.get(f"/users/stores/{first_id}")
            services_resp.raise_for_status()
            services = services_resp.json().get("services") or []
            if len(services) >= 2:
                tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
                await client.post(
                    "/users/bookings/",
                    json={
                        "store_id": first_id,
                        "service_id": services[0]["id"],
                        "customer_name": "Alice",
                        "start_time": tomorrow.replace(
                            hour=10, minute=0, second=0
                        ).isoformat(),
                    },
                )
                bob = await client.post(
                    "/users/bookings/",
                    json={
                        "store_id": first_id,
                        "service_id": services[1]["id"],
                        "customer_name": "Bob",
                        "start_time": tomorrow.replace(
                            hour=14, minute=0, second=0
                        ).isoformat(),
                    },
                )
                bob.raise_for_status()
                await client.patch(
                    f"/owner/bookings/{bob.json()['id']}/status",
                    json={"status": "confirmed"},
                    headers=headers,
                )

        await register_or_login(
            client,
            "customer@test.com",
            "password",
            full_name="Frequent Flyer",
            role="customer",
        )

        total = len(await existing_store_names(client))
        print(f"--- COMPLETE: {total} store(s) in database, {len(created_ids)} created this run ---")


if __name__ == "__main__":
    asyncio.run(main())
