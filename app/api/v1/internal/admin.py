from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.saloon import Store, StoreHours, Service
from app.schemas.saloon import StoreCreate, StoreHoursCreate, ServiceCreate

router = APIRouter(tags=["Internal - Admin"])

ADMIN_TOKEN = "saloon-admin-secret"


class OnboardStoreRequest(BaseModel):
    store: StoreCreate
    hours: List[StoreHoursCreate]
    services: List[ServiceCreate]


class OnboardStoreResponse(BaseModel):
    store_id: UUID
    message: str


async def verify_admin(x_admin_token: Optional[str] = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Admin-Token",
        )


@router.post(
    "/onboard-store",
    response_model=OnboardStoreResponse,
    dependencies=[Depends(verify_admin)],
)
async def onboard_store(
    payload: OnboardStoreRequest, db: AsyncSession = Depends(get_db)
):
    """Bulk creates a store, its hours, and its services in a single transaction."""
    # 1. Create Store
    store = Store(**payload.store.model_dump())
    db.add(store)
    await db.flush()

    # 2. Add Business Hours
    for h_data in payload.hours:
        hours = StoreHours(store_id=store.id, **h_data.model_dump())
        db.add(hours)

    # 3. Add Services
    for s_data in payload.services:
        service = Service(store_id=store.id, **s_data.model_dump())
        db.add(service)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during onboarding: {str(e)}",
        )

    await db.refresh(store)

    return OnboardStoreResponse(
        store_id=store.id,
        message=f"Successfully onboarded '{store.name}' with {len(payload.services)} services.",
    )
