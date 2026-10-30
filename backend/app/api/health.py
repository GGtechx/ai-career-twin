from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.core.database import get_db, engine, Base, get_active_db_info
from app.core.config import settings
from app.schemas.schemas import HealthCheckResponse, DatabaseStatus

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Primary API Health-Check endpoint.
    Verifies API availability, database connection, and created tables count.
    """
    db_info = get_active_db_info()
    db_status = "connected"
    tables_created_count = 0

    try:
        # Execute query to verify live connection
        db.execute(text("SELECT 1"))
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        tables_created_count = len(existing_tables)
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        app_name=settings.PROJECT_NAME,
        database_status=db_status,
        database_type=db_info["active_type"],
        is_sqlite_fallback=db_info["is_sqlite_fallback"],
        configured_db_url_masked=db_info["url_masked"],
        tables_registered_count=len(Base.metadata.tables),
        tables_created_in_db_count=tables_created_count,
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/health/db", response_model=DatabaseStatus)
def database_details(db: Session = Depends(get_db)):
    """
    Detailed diagnostic endpoint returning all created tables in the database.
    """
    db_info = get_active_db_info()
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        return DatabaseStatus(
            connected=True,
            database_type=db_info["active_type"],
            total_tables=len(table_names),
            table_names=table_names,
            details=f"Fallback SQLite active: {db_info['is_sqlite_fallback']}"
        )
    except Exception as e:
        return DatabaseStatus(
            connected=False,
            database_type=db_info["active_type"],
            total_tables=0,
            table_names=[],
            details=f"Connection failed: {str(e)}"
        )
