"""Database Engine & Session Management Module

Sets up production-grade SQLAlchemy engine and session factories, optimized
for Supabase PostgreSQL connection pooling (with auto-ping to handle drops)
and graceful local SQLite support.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""
    pass


# Build Engine with connection parameters tuned for production databases
engine_kwargs = {
    "echo": settings.DEBUG,
}

if settings.is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL / Supabase connection pooling parameters
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields an isolated database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
