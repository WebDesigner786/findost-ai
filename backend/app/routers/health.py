"""System Health & Database Readiness Router"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Verifies API server liveness and database connectivity."""
    db_healthy = False
    db_error = None
    dialect = "unknown"

    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
        dialect = db.bind.dialect.name if db.bind else "unknown"
    except Exception as e:
        db_error = str(e)

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "connected": db_healthy,
            "dialect": dialect,
            "is_supabase_postgres": dialect == "postgresql",
            "error": db_error,
        },
    }
