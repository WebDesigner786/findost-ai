"""Database Seeding Router"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.seed_data import seed_database

router = APIRouter(prefix="/api/seed", tags=["Database Seed"])


@router.post("")
def trigger_database_seed(db: Session = Depends(get_db)):
    """Idempotently seeds the database with the 4 Pakistani financial personas."""
    result = seed_database(db)
    return result
