"""
ORM models for the booking domain.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.saloon import Store, Service

import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditMixin, Base


class BookingStatus(str, Enum):
    """Enforce strict status transitions for bookings."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no-show"


class Booking(AuditMixin, Base):
    """A customer's appointment for a specific service at a store."""

    __tablename__ = "bookings"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    store_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        String(50), nullable=False, default=BookingStatus.PENDING
    )

    # Relationships
    store: Mapped["Store"] = relationship("Store", backref="bookings")
    service: Mapped["Service"] = relationship("Service", backref="bookings")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Booking id={self.id} "
            f"store={self.store_id} "
            f"service={self.service_id} "
            f"status={self.status!r}>"
        )
