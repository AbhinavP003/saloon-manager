from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker, get_db
from app.models.saloon import Service, Store, StoreHours
from app.models.user import User, UserRole

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
