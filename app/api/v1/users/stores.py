from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, Float, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.saloon import Service, Store
from app.schemas.saloon import (
    ServiceRead,
    StoreRead,
    StoreWithDistance,
)

router = APIRouter(tags=["Users - Stores"])


async def _get_store_or_404(store_id: UUID, db: AsyncSession) -> Store:
    result = await db.execute(
        select(Store).where(Store.id == store_id).options(selectinload(Store.services))
    )
    store = result.scalar_one_or_none()
    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store {store_id} not found.",
        )
    return store


@router.get("/", response_model=List[StoreRead], summary="List all stores")
async def list_stores(db: AsyncSession = Depends(get_db)) -> List[Store]:
    result = await db.execute(
        select(Store).options(selectinload(Store.services)).order_by(Store.name)
    )
    return list(result.scalars().all())


@router.get(
    "/nearby", response_model=List[StoreWithDistance], summary="Find stores nearby"
)
async def list_stores_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    earth_radius_km = 6371.0
    lat_col, lon_col = cast(Store.latitude, Float), cast(Store.longitude, Float)
    lat1, lon1 = func.radians(lat), func.radians(lon)
    lat2, lon2 = func.radians(lat_col), func.radians(lon_col)

    distance = (
        func.acos(
            func.sin(lat1) * func.sin(lat2)
            + func.cos(lat1) * func.cos(lat2) * func.cos(lon2 - lon1)
        )
        * earth_radius_km
    )
    distance_calc = distance.label("distance")

    query = (
        select(Store, distance_calc)
        .where(distance <= radius_km)
        .options(selectinload(Store.services))
        .order_by(distance)
    )
    result = await db.execute(query)

    stores_with_distance = []
    for row in result.all():
        store_dict = StoreRead.model_validate(row.Store).model_dump()
        store_dict["distance"] = row.distance
        stores_with_distance.append(store_dict)
    return stores_with_distance


@router.get("/{store_id}", response_model=StoreRead, summary="Get store details")
async def get_store(store_id: UUID, db: AsyncSession = Depends(get_db)) -> Store:
    return await _get_store_or_404(store_id, db)


@router.get(
    "/{store_id}/services", response_model=List[ServiceRead], summary="List services"
)
async def list_services(
    store_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[Service]:
    await _get_store_or_404(store_id, db)
    result = await db.execute(
        select(Service).where(Service.store_id == store_id).order_by(Service.name)
    )
    return list(result.scalars().all())
