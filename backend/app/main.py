"""FinDost AI — FastAPI Main Application Entry Point

Production-grade FastAPI application powering FinDost AI financial operations.
Integrates strict NUMERIC(14,2) decimal math, CORS middleware, global error
handling envelopes, and Supabase PostgreSQL / SQLite database sessions.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.middleware.cors import setup_cors
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.routers import (
    workspaces,
    transactions,
    udhaar,
    scenarios,
    reports,
    documents,
    health,
    seed,
)
from app.services.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: initializes database tables and seeds demo fixtures."""
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)

    # Seed baseline workspaces if database is unseeded
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade financial operations backend for Pakistani SMEs, households, students, and enterprises.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 1. Setup CORS
setup_cors(app)

# 2. Register Global Error Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 3. Mount API Routers
app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(transactions.router)
app.include_router(udhaar.router)
app.include_router(scenarios.router)
app.include_router(reports.router)
app.include_router(documents.router)
app.include_router(seed.router)


@app.get("/", tags=["Root"])
def root_status():
    """Root status endpoint directing developers to OpenAPI docs."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health": "/api/health",
    }
