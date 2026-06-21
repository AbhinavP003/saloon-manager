from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Optional


from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, get_current_user_optional

from app.models.booking import Booking, BookingStatus
from app.models.saloon import Service, Store, StoreHours
from app.schemas.booking import BookingCreate, BookingRead, AvailableSlot
from app.models.user import User

router = APIRouter(tags=["Users - Bookings"])


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> Booking:
    """Customers use this to book a slot. Links to user account if logged in."""
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
    booking_data = payload.model_dump()
    if current_user:
        booking_data["user_id"] = current_user.id

    booking = Booking(**booking_data, end_time=end_time)
    db.add(booking)
    await db.commit()

    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking.id)
        .options(selectinload(Booking.store), selectinload(Booking.service))
    )
    return result.scalar_one()


@router.get(
    "/store/{store_id}/slots",
    response_model=list[AvailableSlot],
    summary="Get available slots for a store/service on a given date",
)
async def get_available_slots(
    store_id: UUID,
    service_id: UUID,
    target_date: date,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Finds all open 30-minute interval slots that can fit the requested service."""

    # 1. Verify store and service
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    service = await db.get(Service, service_id)
    if not service or service.store_id != store_id:
        raise HTTPException(status_code=400, detail="Invalid service for this store.")

    # 2. Get business hours for that day of the week
    day_of_week = target_date.weekday()
    hours = await db.scalar(
        select(StoreHours).where(
            StoreHours.store_id == store_id,
            StoreHours.day_of_week == day_of_week,
        )
    )
    if not hours or hours.is_closed:
        return []

    # 3. Fetch all active bookings for this date to check for overlaps
    # We create datetime bounds covering the entire target day in UTC (or naive, depending on DB tz)
    # The models are DateTime(timezone=True), so we must query with UTC aware instances.
    day_start = datetime.combine(target_date, hours.open_time).replace(
        tzinfo=timezone.utc
    )
    day_end = datetime.combine(target_date, hours.close_time).replace(
        tzinfo=timezone.utc
    )

    active_bookings = await db.scalars(
        select(Booking).where(
            Booking.store_id == store_id,
            Booking.status != "cancelled",
            Booking.end_time > day_start,
            Booking.start_time < day_end,
        )
    )
    bookings = list(active_bookings.all())

    # 4. Generate slots in 30-minute intervals
    available_slots = []
    current_time = day_start
    interval = timedelta(minutes=30)
    service_duration = timedelta(minutes=service.duration_minutes)

    while current_time + service_duration <= day_end:
        slot_start = current_time
        slot_end = current_time + service_duration

        # Check against all overlapping active bookings
        is_overlapping = False
        for b in bookings:
            b_start = (
                b.start_time.replace(tzinfo=timezone.utc)
                if b.start_time.tzinfo is None
                else b.start_time
            )
            b_end = (
                b.end_time.replace(tzinfo=timezone.utc)
                if b.end_time.tzinfo is None
                else b.end_time
            )
            # Overlap formula: start1 < end2 AND start2 < end1
            if slot_start < b_end and b_start < slot_end:
                is_overlapping = True
                break

        if not is_overlapping:
            available_slots.append({"start_time": slot_start})

        current_time += interval

    return available_slots


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)) -> Booking:
    """Fetch details of a specific booking."""
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.store), selectinload(Booking.service))
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: UUID, db: AsyncSession = Depends(get_db)
) -> Booking:
    """Customers use this to cancel their own booking (outside 2-hour window)."""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # 1. No change needed if already cancelled
    if booking.status == BookingStatus.CANCELLED:
        return booking

    # 2. Protect Terminal States
    if booking.status in {BookingStatus.COMPLETED, BookingStatus.NO_SHOW}:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel a booking that is already {booking.status}.",
        )

    # 3. Time Gate (2hr window)
    now = datetime.now(timezone.utc)
    start_time = (
        booking.start_time.replace(tzinfo=timezone.utc)
        if booking.start_time.tzinfo is None
        else booking.start_time
    )

    if start_time < now + timedelta(hours=2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancellations within 2 hours must be handled via phone with the saloon.",
        )

    # 4. Apply Cancellation
    booking.status = BookingStatus.CANCELLED
    await db.commit()

    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking.id)
        .options(selectinload(Booking.store), selectinload(Booking.service))
    )
    return result.scalar_one()


@router.get("/", response_model=list[BookingRead])
async def list_my_bookings(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Booking]:
    """Retrieves all appointments linked to the authenticated user."""
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == current_user.id)
        .options(selectinload(Booking.store), selectinload(Booking.service))
        .order_by(Booking.start_time.desc())
    )
    return list(result.scalars().all())
