"""
FastAPI router for Booking CRUD endpoints.
"""

from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.booking import Booking
from app.models.saloon import Service, Store, StoreHours
from app.schemas.booking import BookingCreate, BookingRead

router = APIRouter(tags=["bookings"])


@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
)
async def create_booking(
    payload: BookingCreate,
    db: AsyncSession = Depends(get_db),
) -> Booking:
    """Create a new booking after validating store and service constraints."""

    # 1. Verify store exists
    store = await db.get(Store, payload.store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store {payload.store_id} not found.",
        )

    # 2. Verify service exists AND belongs to the specified store
    service = await db.get(Service, payload.service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {payload.service_id} not found.",
        )

    if service.store_id != payload.store_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service {payload.service_id} does not belong to Store {payload.store_id}.",
        )

    # 3. Calculate end_time
    end_time = payload.start_time + timedelta(minutes=service.duration_minutes)

    # 4. Enforce Store Hours
    day_of_week = payload.start_time.weekday()  # 0 = Monday, 6 = Sunday
    booking_time_only = payload.start_time.time()
    end_time_only = end_time.time()

    hours = await db.scalar(
        select(StoreHours).where(
            StoreHours.store_id == payload.store_id,
            StoreHours.day_of_week == day_of_week,
        )
    )
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store hours are not configured for this day.",
        )
    if hours.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store is closed on this day.",
        )
    if booking_time_only < hours.open_time or end_time_only > hours.close_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking ({booking_time_only} - {end_time_only}) falls outside operating hours ({hours.open_time} - {hours.close_time}).",
        )

    # 5. Check overlaps
    # Overlap condition: new_start < existing_end AND new_end > existing_start
    overlap_query = select(Booking).where(
        Booking.store_id == payload.store_id,
        Booking.status != "cancelled",
        Booking.start_time < end_time,
        Booking.end_time > payload.start_time,
    )
    overlap = await db.scalar(overlap_query)
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot is already booked for this store.",
        )

    # 6. Create booking
    booking = Booking(**payload.model_dump(), end_time=end_time)
    db.add(booking)
    await db.flush()
    await db.refresh(booking)
    return booking


@router.get(
    "/store/{store_id}",
    response_model=List[BookingRead],
    summary="List bookings for a specific store",
)
async def list_store_bookings(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[Booking]:
    """Return all bookings for a given store, ordered by booking time."""

    # Verify store exists
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store {store_id} not found.",
        )

    result = await db.execute(
        select(Booking).where(Booking.store_id == store_id).order_by(Booking.start_time)
    )
    return list(result.scalars().all())
