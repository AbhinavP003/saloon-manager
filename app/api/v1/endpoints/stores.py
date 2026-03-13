"""
FastAPI router for Store CRUD endpoints, including nested Service sub-resources.

Routes
------
POST   /api/v1/stores/                          – create store
GET    /api/v1/stores/                          – list all stores
GET    /api/v1/stores/{store_id}                – get single store (with services)
POST   /api/v1/stores/{store_id}/services       – add service to store
GET    /api/v1/stores/{store_id}/services       – list services of a store
"""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, Float, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.saloon import Service, Store
from app.schemas.saloon import (
    ServiceCreate,
    ServiceRead,
    StoreCreate,
    StoreRead,
    StoreWithDistance,
)

router = APIRouter(tags=["stores"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_store_or_404(store_id: UUID, db: AsyncSession) -> Store:
    """Fetch a Store by PK with its services eagerly loaded, or raise 404."""
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


# ---------------------------------------------------------------------------
# POST /stores/
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=StoreRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store",
)
async def create_store(
    payload: StoreCreate,
    db: AsyncSession = Depends(get_db),
) -> Store:
    """Create a new saloon store and persist it to the database."""
    store = Store(**payload.model_dump())
    db.add(store)
    await db.flush()  # populate DB-generated fields (id, created_at, …)
    await db.refresh(store, attribute_names=["services"])
    return store


# ---------------------------------------------------------------------------
# GET /stores/
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=List[StoreRead],
    summary="List all stores",
)
async def list_stores(
    db: AsyncSession = Depends(get_db),
) -> List[Store]:
    """Return all stores ordered by name, each including their services."""
    result = await db.execute(
        select(Store).options(selectinload(Store.services)).order_by(Store.name)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# GET /stores/nearby
# ---------------------------------------------------------------------------


@router.get(
    "/nearby",
    response_model=List[StoreWithDistance],
    summary="List stores ordered by distance from a given point",
)
async def list_stores_nearby(
    lat: float = Query(..., ge=-90, le=90, description="Search latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Search longitude"),
    radius_km: float = Query(10.0, gt=0, description="Max search radius in kilometers"),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Return stores within a radius, including the calculated distance in kilometers."""
    # Earth's radius in kilometers
    earth_radius_km = 6371.0

    # Haversine formula built with SQLAlchemy func:
    # distance = acos(
    #   sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1)
    # ) * R
    lat_col = cast(Store.latitude, Float)
    lon_col = cast(Store.longitude, Float)

    # Convert everything to radians
    lat1 = func.radians(lat)
    lon1 = func.radians(lon)
    lat2 = func.radians(lat_col)
    lon2 = func.radians(lon_col)

    distance = (
        func.acos(
            func.sin(lat1) * func.sin(lat2)
            + func.cos(lat1) * func.cos(lat2) * func.cos(lon2 - lon1)
        )
        * earth_radius_km
    )

    # Alias the distance expression so we can use it in both SELECT and WHERE
    distance_calc = distance.label("distance")

    query = (
        select(Store, distance_calc)
        .where(distance <= radius_km)
        .options(selectinload(Store.services))
        .order_by(distance)
    )

    result = await db.execute(query)

    # We need to reshape the results since we requested both Store and distance.
    # We return a list of dicts reflecting the StoreWithDistance schema.
    stores_with_distance = []
    for row in result.all():
        store_obj = row.Store
        # Note: distance comes out as a float directly
        dist = row.distance

        # We manually construct a dict representing the Pydantic schema shape
        # SQLAlchemy models have __dict__, but it includes private SA state.
        # It's cleaner to let Pydantic model_validate / from_attributes handle
        # the store object, and we just append the extra field.

        # Easiest way in FastAPI V2 is to return the object + attribute, or just
        # let Pydantic construct it if we pass it a dict matching StoreWithDistance
        store_dict = StoreRead.model_validate(store_obj).model_dump()
        store_dict["distance"] = dist
        stores_with_distance.append(store_dict)

    return stores_with_distance


# ---------------------------------------------------------------------------
# GET /stores/{store_id}
# ---------------------------------------------------------------------------


@router.get(
    "/{store_id}",
    response_model=StoreRead,
    summary="Retrieve a store by ID",
)
async def get_store(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Store:
    """Return a single store with its services, or 404 if not found."""
    return await _get_store_or_404(store_id, db)


# ---------------------------------------------------------------------------
# POST /stores/{store_id}/services
# ---------------------------------------------------------------------------


@router.post(
    "/{store_id}/services",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a service to a store",
)
async def create_service(
    store_id: UUID,
    payload: ServiceCreate,
    db: AsyncSession = Depends(get_db),
) -> Service:
    """Verify the store exists, then create a service linked to it."""
    # Verify parent store exists (raises 404 if not)
    await _get_store_or_404(store_id, db)

    service = Service(**payload.model_dump(), store_id=store_id)
    db.add(service)
    await db.flush()
    await db.refresh(service)
    return service


# ---------------------------------------------------------------------------
# GET /stores/{store_id}/services
# ---------------------------------------------------------------------------


@router.get(
    "/{store_id}/services",
    response_model=List[ServiceRead],
    summary="List all services for a store",
)
async def list_services(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[Service]:
    """Return all services belonging to the given store, ordered by name."""
    # Verify parent store exists (raises 404 if not)
    await _get_store_or_404(store_id, db)

    result = await db.execute(
        select(Service).where(Service.store_id == store_id).order_by(Service.name)
    )
    return list(result.scalars().all())
