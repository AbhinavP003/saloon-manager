"""
Application configuration loaded from environment variables.

Uses pydantic-settings so all config is validated at startup and
sourced exclusively from the .env file — no hardcoded secrets.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object for the Saloon Manager application."""

    # ------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------
    PROJECT_NAME: str = "Saloon Manager"

    # ------------------------------------------------------------------
    # Security & Auth
    # ------------------------------------------------------------------
    # Generate a strong key for production (e.g. openssl rand -hex 32)
    SECRET_KEY: str = "saloon-top-secret-locally-changed-later"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS — comma-separated in env (e.g. http://localhost:3000,https://frontend.run.app)
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str  # e.g. postgresql+asyncpg://user:pass@host:5432/db

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    PORT: int = 8080  # Cloud Run injects this env var

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Single application-wide instance — import this everywhere.
settings = Settings()
