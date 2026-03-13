"""
ORM models for the core saloon domain.

Models
------
Store   – a physical saloon location.
Service – a treatment/service offered by a store.

Both models inherit from Base (which provides the SQLAlchemy registry) and
AuditMixin (which contributes created_at, updated_at, created_by, updated_by).
"""

import uuid
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditMixin, Base


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


class Store(AuditMixin, Base):
    """A physical saloon location."""

    __tablename__ = "stores"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Core fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    contact_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, default=None
    )

    # Geospatial coordinates (used for nearest-store logic)
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=9, scale=6), nullable=True, default=None
    )
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=9, scale=6), nullable=True, default=None
    )

    # Relationships
    services: Mapped[List["Service"]] = relationship(
        "Service",
        back_populates="store",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Store id={self.id} name={self.name!r}>"


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class Service(AuditMixin, Base):
    """A treatment or service offered by a store."""

    __tablename__ = "services"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Core fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, default=None
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Foreign key
    store_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    store: Mapped["Store"] = relationship(
        "Store",
        back_populates="services",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Service id={self.id} name={self.name!r} store_id={self.store_id}>"
