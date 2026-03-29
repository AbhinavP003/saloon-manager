from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Saloon Manager")

# Allow CORS for local frontend development

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This one line includes everything!
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok", "service": "saloon-manager"}
