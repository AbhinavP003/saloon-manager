"""
FastAPI router for Store CRUD endpoints.

Mounted under /api/v1/stores in app/main.py.
"""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.saloon import Store
from app.schemas.saloon import StoreCreate, StoreRead

router = APIRouter(tags=["stores"])


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
    await db.refresh(store)
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
    """Return all stores ordered by name."""
    result = await db.execute(select(Store).order_by(Store.name))
    return list(result.scalars().all())


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
    """Return a single store, or 404 if not found."""
    store = await db.get(Store, store_id)
    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store {store_id} not found.",
        )
    return store
