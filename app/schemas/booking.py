"""
Pydantic schemas for the booking domain.
"""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookingBase(BaseModel):
    """Fields shared across all Booking schema variants."""

    store_id: UUID
    service_id: UUID
    customer_name: Annotated[
        str, Field(min_length=1, max_length=255, examples=["John Doe"])
    ]
    start_time: Annotated[datetime, Field(examples=["2026-03-20T10:00:00Z"])]


class BookingCreate(BookingBase):
    """Payload required to create a new Booking."""

    # Optional explicitly provided status on create, though it defaults to pending
    status: Annotated[
        Optional[str], Field(default="pending", max_length=50, examples=["pending"])
    ]


class BookingRead(BookingBase):
    """Booking representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime


class AvailableSlot(BaseModel):
    """Represents a single available 30-minute booking slot."""

    start_time: datetime
