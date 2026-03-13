"""
ORM models for the booking domain.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.saloon import Store, Service

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditMixin, Base


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
    booking_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

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
