"""
Async database engine, session factory, and shared base classes.

- Engine is created from settings.DATABASE_URL at module import time.
- get_db() is a FastAPI dependency that yields a per-request AsyncSession
  and commits / rolls back automatically.
- AuditMixin adds created_at, updated_at, created_by, updated_by to every
  model that inherits from it (including Base-derived models).
"""

from uuid import UUID
from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # set True locally if you want SQL logs
    pool_pre_ping=True,  # recycle stale connections automatically
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for the duration of a single request.

    Usage::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base.

    All ORM models should inherit from this class.
    """


# ---------------------------------------------------------------------------
# Audit mixin
# ---------------------------------------------------------------------------


class AuditMixin:
    """Mixin that adds standard audit columns to any model.

    Mix in *after* ``Base`` so that ``__tablename__`` resolution works::

        class MyModel(AuditMixin, Base):
            __tablename__ = "my_model"
            ...
    """

    created_at: Mapped[Optional[str]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Optional[str]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[UUID]] = mapped_column(
        Uuid(),
        nullable=True,
        default=None,
    )
    updated_by: Mapped[Optional[UUID]] = mapped_column(
        Uuid(),
        nullable=True,
        default=None,
    )
