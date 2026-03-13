from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.saloon import Service, Store, StoreHours
from app.schemas.saloon import (
    ServiceCreate,
    ServiceRead,
    StoreCreate,
    StoreRead,
    StoreHoursCreate,
    StoreHoursRead,
)

router = APIRouter(tags=["Owner - Stores"])


@router.post("/", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
async def create_store(
    payload: StoreCreate, db: AsyncSession = Depends(get_db)
) -> Store:
    store = Store(**payload.model_dump())
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
    store_id: UUID, payload: ServiceCreate, db: AsyncSession = Depends(get_db)
) -> Service:
    # Check if store exists
    store_check = await db.get(Store, store_id)
    if not store_check:
        raise HTTPException(status_code=404, detail="Store not found")

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
    store_id: UUID, payload: StoreHoursCreate, db: AsyncSession = Depends(get_db)
) -> StoreHours:
    """Fixes the 404 in your tests by allowing owners to set store hours."""
    hour = StoreHours(**payload.model_dump(), store_id=store_id)
    db.add(hour)
    await db.commit()
    await db.refresh(hour)
    return hour
