"""
Application configuration loaded from environment variables.

Uses pydantic-settings so all config is validated at startup and
sourced exclusively from the .env file — no hardcoded secrets.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object for the Saloon Manager application."""

    # ------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------
    PROJECT_NAME: str = "Saloon Manager"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str  # e.g. postgresql+asyncpg://user:pass@host:5432/db

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Single application-wide instance — import this everywhere.
settings = Settings()
