"""
Database model for application users.
"""

import uuid
from enum import Enum
from uuid import UUID

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditMixin, Base


class UserRole(str, Enum):
    """Supported roles for RBAC in the saloon marketplace."""

    CUSTOMER = "customer"
    STORE_OWNER = "owner"
    ADMIN = "admin"


class User(AuditMixin, Base):
    """Representation of an authenticated user."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Core identity fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Permissions & Flags
    role: Mapped[UserRole] = mapped_column(
        String(50), nullable=False, default=UserRole.CUSTOMER
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User email={self.email!r} role={self.role!r}>"
