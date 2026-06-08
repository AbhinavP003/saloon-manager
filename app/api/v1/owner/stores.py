from calendar import monthrange
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import RoleChecker, get_db
from app.models.booking import Booking, BookingStatus
from app.models.saloon import Service, Store, StoreHours
from app.models.user import User, UserRole
from app.schemas.analytics import HourlyCount, StoreAnalytics
from app.schemas.saloon import (
    ServiceCreate,
    ServiceRead,
    StoreCreate,
    StoreRead,
    StoreHoursCreate,
    StoreHoursRead,
)

router = APIRouter(
    tags=["Owner - Stores"],
)


@router.post("/", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
async def create_store(
    payload: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[
        User, Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))
    ] = None,
) -> Store:
    store = Store(**payload.model_dump(), owner_id=current_user.id)
    db.add(store)
    await db.commit()

    await db.refresh(
        store,
        attribute_names=[
            "services",
            "hours",
            "id",
            "name",
            "address",
            "contact_number",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ],
    )

    return store


@router.post(
    "/{store_id}/services",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_service(
    store_id: UUID,
    payload: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[
        User, Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))
    ] = None,
) -> Service:
    # Check if store exists and user owns it
    store_check = await db.get(Store, store_id)
    if not store_check:
        raise HTTPException(status_code=404, detail="Store not found")

    if store_check.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized for this salon.")

    service = Service(**payload.model_dump(), store_id=store_id)
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.post(
    "/{store_id}/store-hours",
    response_model=StoreHoursRead,
    status_code=status.HTTP_201_CREATED,
)
async def set_operating_hours(
    store_id: UUID,
    payload: StoreHoursCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[
        User, Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))
    ] = None,
) -> StoreHours:
    # Check ownership
    store_check = await db.get(Store, store_id)
    if not store_check or (
        store_check.owner_id != current_user.id and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Not authorized for this salon.")

    """Fixes the 404 in your tests by allowing owners to set store hours."""
    hour = StoreHours(**payload.model_dump(), store_id=store_id)
    db.add(hour)
    await db.commit()
    await db.refresh(hour)
    return hour


@router.get("/{store_id}/analytics", response_model=StoreAnalytics)
async def get_store_analytics(
    store_id: UUID,
    month: Annotated[str, Query(pattern=r"^\d{4}-\d{2}$", examples=["2026-06"])],
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[
        User, Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.ADMIN]))
    ] = None,
) -> StoreAnalytics:
    """Monthly revenue and busy-hour report for completed bookings."""
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    if store.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized for this salon.")

    year, month_num = map(int, month.split("-"))
    last_day = monthrange(year, month_num)[1]
    period_start = datetime(year, month_num, 1, tzinfo=timezone.utc)
    period_end = datetime(
        year, month_num, last_day, 23, 59, 59, tzinfo=timezone.utc
    )

    result = await db.execute(
        select(Booking)
        .where(
            Booking.store_id == store_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.start_time >= period_start,
            Booking.start_time <= period_end,
        )
        .options(selectinload(Booking.service))
    )
    completed = list(result.scalars().all())

    revenue = sum(
        (b.service.price if b.service else Decimal("0")) for b in completed
    )
    hour_counts: dict[int, int] = {h: 0 for h in range(24)}
    for booking in completed:
        hour_counts[booking.start_time.hour] += 1

    busy_hours = [
        HourlyCount(hour=h, count=hour_counts[h])
        for h in sorted(hour_counts, key=hour_counts.get, reverse=True)
        if hour_counts[h] > 0
    ]

    return StoreAnalytics(
        month=month,
        completed_bookings=len(completed),
        monthly_revenue=revenue,
        busy_hours=busy_hours,
    )
