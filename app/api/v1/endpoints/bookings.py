"""
FastAPI router for Booking CRUD endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.booking import Booking
from app.models.saloon import Service, Store
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

    # 3. Create booking
    booking = Booking(**payload.model_dump())
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
        select(Booking)
        .where(Booking.store_id == store_id)
        .order_by(Booking.booking_time)
    )
    return list(result.scalars().all())
