"""Application Configuration Module

Uses Pydantic BaseSettings to load environment variables safely with zero
hardcoded credentials. Adapts PostgreSQL connection strings (e.g. Supabase)
to standard SQLAlchemy dialect format.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General Environment
    PROJECT_NAME: str = "FinDost AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Allowed Origins
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Database Configuration (Supabase PostgreSQL / SQLite fallback)
    DATABASE_URL: str = "sqlite:///./findost_local.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if not v:
            return "sqlite:///./findost_local.db"
        # Supabase and Heroku historically emit postgres:// - SQLAlchemy 2.0 requires postgresql://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # Connection Pooling Settings (Critical for Supabase PgBouncer / Transaction pooler)
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_PRE_PING: bool = True

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    # Auth & Headers
    DEMO_USER_HEADER: str = "X-Demo-User"
    DEFAULT_DEMO_USER: str = "demo-findost-judge"
    JWT_SECRET_KEY: str = Field(default="change-me-in-production-use-secure-random-token")
    JWT_ALGORITHM: str = "HS256"


# Singleton instance
settings = Settings()
