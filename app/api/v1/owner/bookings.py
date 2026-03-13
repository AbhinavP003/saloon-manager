from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.booking import Booking
from app.models.saloon import Store
from app.schemas.booking import BookingRead

router = APIRouter(tags=["Owner - Bookings"])


@router.get("/store/{store_id}", response_model=List[BookingRead])
async def list_store_bookings(
    store_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[Booking]:
    """Owners use this to see their saloon's schedule."""
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    result = await db.execute(
        select(Booking).where(Booking.store_id == store_id).order_by(Booking.start_time)
    )
    return list(result.scalars().all())


# Future Owner Endpoints:
# @router.patch("/{booking_id}/cancel")
# @router.patch("/{booking_id}/complete")
