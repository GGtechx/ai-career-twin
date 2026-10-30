"""
Database Initialization Script for AI Digital Career Twin
Creates all 21 tables in the active database (PostgreSQL or SQLite fallback).
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import engine, Base, active_db_type, get_active_db_info
import app.models  # Registers all 21 models
from sqlalchemy import inspect

def init_database():
    print("=" * 60)
    print("AI Digital Career Twin - Database Initializer")
    print("=" * 60)
    
    info = get_active_db_info()
    print(f"Configured Database URL: {info['configured_url']}")
    print(f"Active Engine Type:      {info['active_type']}")
    print(f"SQLite Fallback Active:  {info['is_sqlite_fallback']}")
    print("-" * 60)

    print(f"Registering {len(Base.metadata.tables)} models:")
    for idx, table_name in enumerate(sorted(Base.metadata.tables.keys()), 1):
        print(f"  {idx:2d}. {table_name}")

    print("-" * 60)
    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Verify via inspector
    inspector = inspect(engine)
    created_tables = inspector.get_table_names()
    print(f"\nVerification: {len(created_tables)} tables confirmed present in database:")
    for t in sorted(created_tables):
        print(f"  [OK] {t}")
    print("=" * 60)

if __name__ == "__main__":
    init_database()
