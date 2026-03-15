from fastapi import FastAPI
from app.api.v1.api import api_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Saloon Manager")

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This one line includes everything!
app.include_router(api_router, prefix="/api/v1")
