from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker, get_db
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.models.saloon import Store
from app.schemas.booking import BookingRead, StatusUpdate

router = APIRouter(
    tags=["Owner - Bookings"],
    dependencies=[Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))],
)


@router.get("/store/{store_id}", response_model=List[BookingRead])
async def list_store_bookings(
    store_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        User, Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))
    ],
) -> List[Booking]:
    """Owners use this to see their saloon's schedule."""
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    # Ownership Check (New in Phase 4)
    if store.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized for this salon.")

    result = await db.execute(
        select(Booking)
        .where(Booking.store_id == store_id)
        .options(selectinload(Booking.store), selectinload(Booking.service))
        .order_by(Booking.start_time)
    )

    return list(result.scalars().all())


@router.patch("/{booking_id}/status", response_model=BookingRead)
async def update_booking_status(
    booking_id: UUID,
    payload: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[
        User, Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))
    ] = None,
) -> Booking:
    """Owners use this to transition a booking (Confirm, Complete, etc)."""
    # Load booking with store to check ownership
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.store))
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Ownership Check
    if (
        booking.store.owner_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Not authorized for this booking.")

    old_status = booking.status
    new_status = payload.status

    # 1. Protect Terminal States
    terminal_states = {
        BookingStatus.CANCELLED,
        BookingStatus.COMPLETED,
        BookingStatus.NO_SHOW,
    }
    if old_status in terminal_states:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update status from terminal state: {old_status}",
        )

    # 2. Validate Transitions
    # Define allowed 'From -> To' paths
    allowed_transitions = {
        BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
        BookingStatus.CONFIRMED: [
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
            BookingStatus.NO_SHOW,
        ],
    }

    if new_status not in allowed_transitions.get(old_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {old_status} to {new_status}",
        )

    # 3. Apply change
    booking.status = new_status
    await db.commit()

    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.store), selectinload(Booking.service))
    )
    return result.scalar_one()
