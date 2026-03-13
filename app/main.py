"""
FastAPI application entry point for Saloon Manager.
"""

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.endpoints.stores import router as stores_router
from app.api.v1.endpoints.bookings import router as bookings_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# API v1 routes
# ---------------------------------------------------------------------------

app.include_router(stores_router, prefix="/api/v1/stores", tags=["stores"])
app.include_router(bookings_router, prefix="/api/v1/bookings", tags=["bookings"])
