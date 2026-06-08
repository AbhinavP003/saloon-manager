"""
Application configuration loaded from environment variables.

Uses pydantic-settings so all config is validated at startup and
sourced exclusively from the .env file — no hardcoded secrets.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.debug_log import debug_log


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
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
            return origins or ["http://localhost:3000"]
        return value

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str  # e.g. postgresql+asyncpg://user:pass@host:5432/db

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def strip_database_url(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def ensure_asyncpg_driver(cls, value: str) -> str:
        """Cloud SQL secrets often use postgres:// or postgresql:// — need +asyncpg."""
        if value.startswith("sqlite"):
            return value
        if value.startswith("postgresql+asyncpg://"):
            return value
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value[len("postgresql://") :]
        return value

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
# #region agent log
debug_log("config.py:settings", "loading_settings_start", {}, "H2")
# #endregion
try:
    settings = Settings()
    # #region agent log
    debug_log(
        "config.py:settings",
        "loading_settings_ok",
        {
            "has_database_url": bool(settings.DATABASE_URL),
            "database_scheme": settings.DATABASE_URL.split(":", 1)[0],
            "cors_count": len(settings.BACKEND_CORS_ORIGINS),
            "port": settings.PORT,
        },
        "H2",
    )
    # #endregion
except Exception as exc:
    # #region agent log
    debug_log(
        "config.py:settings",
        "loading_settings_failed",
        {"error_type": type(exc).__name__, "error": str(exc)},
        "H2",
    )
    # #endregion
    raise
