"""
Pydantic schemas for the saloon domain.

Schemas are split into three tiers:
  Base   – shared field definitions and validation rules.
  Create – payload accepted on write operations (POST/PUT).
  Read   – payload returned from the API (includes DB-generated fields).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Store schemas
# ---------------------------------------------------------------------------


class StoreBase(BaseModel):
    """Fields shared across all Store schema variants."""

    name: str = Field(..., max_length=255, examples=["Downtown Cuts"])
    address: str = Field(..., max_length=500, examples=["123 Main St, City"])
    contact_number: Optional[str] = Field(
        default=None, max_length=20, examples=["+91-9876543210"]
    )
    latitude: Optional[Decimal] = Field(
        default=None,
        ge=-90,
        le=90,
        decimal_places=6,
        examples=[12.971599],
    )
    longitude: Optional[Decimal] = Field(
        default=None,
        ge=-180,
        le=180,
        decimal_places=6,
        examples=[77.594566],
    )


class StoreCreate(StoreBase):
    """Payload required to create a new Store."""


class StoreRead(StoreBase):
    """Store representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
