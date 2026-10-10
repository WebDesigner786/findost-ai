"""CLI Script to Initialize and Seed FinDost AI Database

Usage:
    cd backend
    python scripts/init_db.py
"""

import sys
import os

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database
from app.config import settings


def main():
    print(f"Connecting to database via: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print("Creating all database tables (workspaces, documents, transactions, udhaar, forecasts, anomalies, recommendations)...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables successfully created.")

    print("Seeding baseline financial fixtures for Pakistani personas...")
    db = SessionLocal()
    try:
        result = seed_database(db)
        print(f"[OK] {result['message']}")
    finally:
        db.close()

    print("\nDatabase initialization complete! Ready for FastAPI server.")


if __name__ == "__main__":
    main()
