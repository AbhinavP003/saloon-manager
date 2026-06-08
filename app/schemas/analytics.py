"""Pydantic schemas for owner analytics."""

from decimal import Decimal

from pydantic import BaseModel, Field


class HourlyCount(BaseModel):
    """Booking count for a single hour of the day (0–23)."""

    hour: int = Field(ge=0, le=23)
    count: int = Field(ge=0)


class StoreAnalytics(BaseModel):
    """Monthly revenue and busy-hour summary for a store."""

    month: str
    completed_bookings: int
    monthly_revenue: Decimal
    busy_hours: list[HourlyCount]
