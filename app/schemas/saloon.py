"""
Pydantic schemas for the saloon domain.

Schemas are split into three tiers:
  Base   – shared field definitions and validation rules.
  Create – payload accepted on write operations (POST/PUT).
  Read   – payload returned from the API (includes DB-generated fields).
"""

from datetime import time
from decimal import Decimal
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from app.schemas.common import AuditSchema


# ---------------------------------------------------------------------------
# Service schemas  (defined before StoreRead to avoid forward-ref rebuilds)
# ---------------------------------------------------------------------------


class ServiceBase(BaseModel):
    """Fields shared across all Service schema variants."""

    name: Annotated[str, Field(min_length=1, max_length=255, examples=["Haircut"])]
    description: Annotated[
        Optional[str],
        Field(
            default=None,
            min_length=1,
            max_length=1000,
            examples=["Classic scissor cut"],
        ),
    ]
    price: Annotated[Decimal, Field(gt=0, decimal_places=2, examples=[250.00])]
    duration_minutes: Annotated[int, Field(ge=5, examples=[30])]


class ServiceCreate(ServiceBase):
    """Payload required to create a new Service.

    store_id is supplied via the URL path, not the request body.
    """


# ---------------------------------------------------------------------------
# Store schemas
# ---------------------------------------------------------------------------


class StoreBase(BaseModel):
    """Fields shared across all Store schema variants."""

    name: Annotated[str, Field(min_length=1, max_length=255)]
    address: Annotated[str, Field(min_length=1, max_length=500)]
    contact_number: Optional[str] = Field(default=None, max_length=20)

    # Change these to allow plain float/decimal without strict decimal_places
    # during serialization from the DB.
    latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180)


class StoreCreate(StoreBase):
    """Payload required to create a new Store."""


class StoreHoursBase(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    open_time: time
    close_time: time
    is_closed: bool = False


class StoreHoursCreate(StoreHoursBase):
    pass


# --- StoreHours ---
class StoreHoursRead(StoreHoursBase, AuditSchema):
    id: UUID
    store_id: UUID


# --- Service ---
class ServiceRead(ServiceBase, AuditSchema):
    id: UUID
    store_id: UUID


# --- Store ---
class StoreRead(StoreBase, AuditSchema):
    id: UUID
    services: List[ServiceRead] | None = Field(default_factory=list)


class StoreWithDistance(StoreRead, AuditSchema):
    """Store representation that includes the calculated distance from a search point."""

    distance: float = Field(..., description="Distance in kilometers")
