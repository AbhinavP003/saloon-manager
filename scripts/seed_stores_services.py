import asyncio
from datetime import time
from app.core.database import AsyncSessionLocal
from app.models.saloon import Store, Service, StoreHours


async def seed_data():
    async with AsyncSessionLocal() as session:
        print("🌱 Seeding database...")

        # 1. Create Stores
        stores = [
            Store(
                name="Kakkanad Premium Saloon",
                address="Near Civil Station",
                latitude=10.017,
                longitude=76.344,
                contact_number="9876543210",
            ),
            Store(
                name="Edappally Grooming Hub",
                address="Near Lulu Mall",
                latitude=10.027,
                longitude=76.308,
                contact_number="9876543211",
            ),
            Store(
                name="Panampilly Styles",
                address="Main Ave",
                latitude=9.963,
                longitude=76.294,
                contact_number="9876543212",
            ),
        ]
        session.add_all(stores)
        await session.flush()  # Push to DB to get IDs

        # 2. Add Business Hours for all stores (Mon-Sat, 9 AM - 9 PM)
        for store in stores:
            for day in range(0, 6):  # Monday to Saturday
                hours = StoreHours(
                    store_id=store.id,
                    day_of_week=day,
                    open_time=time(9, 0),
                    close_time=time(21, 0),
                    is_closed=False,
                )
                session.add(hours)

        # 3. Add Services to Stores
        for store in stores:
            services = [
                Service(
                    name="Classic Haircut",
                    description="Precision cut",
                    price=300.0,
                    duration_minutes=30,
                    store_id=store.id,
                ),
                Service(
                    name="Luxury Shave",
                    description="Hot towel treatment",
                    price=250.0,
                    duration_minutes=20,
                    store_id=store.id,
                ),
                Service(
                    name="Full Grooming",
                    description="Hair + Beard + Facial",
                    price=1200.0,
                    duration_minutes=90,
                    store_id=store.id,
                ),
            ]
            session.add_all(services)

        await session.commit()
        print("✅ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())
