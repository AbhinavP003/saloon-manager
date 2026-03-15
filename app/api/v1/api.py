from fastapi import APIRouter
from app.api.v1.users import stores as user_stores, bookings as user_bookings
from app.api.v1.owner import stores as owner_stores, bookings as owner_bookings
from app.api.v1.internal import admin as internal_admin

api_router = APIRouter()

# --- Users Namespace ---
api_router.include_router(user_stores.router, prefix="/users/stores")
api_router.include_router(user_bookings.router, prefix="/users/bookings")

# --- Owner Namespace ---
api_router.include_router(owner_stores.router, prefix="/owner/stores")
api_router.include_router(owner_bookings.router, prefix="/owner/bookings")

# --- Internal/Admin Namespace ---
api_router.include_router(internal_admin.router, prefix="/internal")
