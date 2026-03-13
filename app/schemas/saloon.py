"""
Pydantic schemas for the saloon domain.

Schemas are split into three tiers:
  Base   – shared field definitions and validation rules.
  Create – payload accepted on write operations (POST/PUT).
  Read   – payload returned from the API (includes DB-generated fields).
"""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class ServiceRead(ServiceBase):
    """Service representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    store_id: UUID


# ---------------------------------------------------------------------------
# Store schemas
# ---------------------------------------------------------------------------


class StoreBase(BaseModel):
    """Fields shared across all Store schema variants."""

    name: Annotated[
        str, Field(min_length=1, max_length=255, examples=["Downtown Cuts"])
    ]
    address: Annotated[
        str, Field(min_length=1, max_length=500, examples=["123 Main St, City"])
    ]
    contact_number: Annotated[
        Optional[str],
        Field(default=None, min_length=1, max_length=20, examples=["+91-9876543210"]),
    ]
    latitude: Annotated[
        Optional[Decimal],
        Field(default=None, ge=-90, le=90, decimal_places=6, examples=[12.971599]),
    ]
    longitude: Annotated[
        Optional[Decimal],
        Field(default=None, ge=-180, le=180, decimal_places=6, examples=[77.594566]),
    ]


class StoreCreate(StoreBase):
    """Payload required to create a new Store."""


class StoreRead(StoreBase):
    """Store representation returned by the API.

    The ``services`` field is populated only when the relationship is
    eagerly loaded (selectinload); it defaults to an empty list otherwise.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    services: List[ServiceRead] = Field(default_factory=list)


class StoreWithDistance(StoreRead):
    """Store representation that includes the calculated distance from a search point."""

    distance: float = Field(..., description="Distance in kilometers")
