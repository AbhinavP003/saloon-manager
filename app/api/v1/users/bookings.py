from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.booking import Booking
from app.models.saloon import Service, Store, StoreHours
from app.schemas.booking import BookingCreate, BookingRead

router = APIRouter(tags=["Users - Bookings"])


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate, db: AsyncSession = Depends(get_db)
) -> Booking:
    """Customers use this to book a slot."""
    # 1. Verify store exists
    store = await db.get(Store, payload.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    # 2. Verify service belongs to store
    service = await db.get(Service, payload.service_id)
    if not service or service.store_id != payload.store_id:
        raise HTTPException(status_code=400, detail="Invalid service for this store.")

    # 3. Calculate end_time
    end_time = payload.start_time + timedelta(minutes=service.duration_minutes)

    # 4. Enforce Store Hours
    day_of_week = payload.start_time.weekday()
    hours = await db.scalar(
        select(StoreHours).where(
            StoreHours.store_id == payload.store_id,
            StoreHours.day_of_week == day_of_week,
        )
    )
    if not hours:
        raise HTTPException(
            status_code=400, detail="Store hours are not configured for this day."
        )

    booking_time = payload.start_time.time()
    if booking_time < hours.open_time or end_time.time() > hours.close_time:
        raise HTTPException(
            status_code=400, detail="Booking falls outside operating hours."
        )

    # 5. Check overlaps
    overlap = await db.scalar(
        select(Booking).where(
            Booking.store_id == payload.store_id,
            Booking.status != "cancelled",
            Booking.start_time < end_time,
            Booking.end_time > payload.start_time,
        )
    )
    if overlap:
        raise HTTPException(status_code=400, detail="Time slot is already booked.")

    # 6. Create booking
    booking = Booking(**payload.model_dump(), end_time=end_time)
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking
