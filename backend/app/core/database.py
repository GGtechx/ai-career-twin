import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

Base = declarative_base()

def init_engine():
    """
    Initializes SQLAlchemy engine.
    Tries PostgreSQL first as configured; if unavailable, falls back to SQLite
    to allow development and testing without blocking.
    """
    db_url = settings.DATABASE_URL
    is_postgres = db_url.startswith("postgresql")
    active_engine = None
    engine_type = "postgresql" if is_postgres else "sqlite"

    if is_postgres:
        try:
            logger.info(f"Attempting PostgreSQL connection: {db_url}")
            test_engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 3}
            )
            # Verify immediate connection
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL database!")
            active_engine = test_engine
            engine_type = "postgresql"
        except Exception as e:
            logger.warning(
                f"PostgreSQL connection failed ({e}). "
                f"Falling back to SQLite: {settings.SQLITE_FALLBACK_URL} for local development."
            )
            active_engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
            engine_type = "sqlite"
    else:
        active_engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
        )
        engine_type = "sqlite" if "sqlite" in db_url else "other"

    return active_engine, engine_type

engine, active_db_type = init_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_active_db_info():
    """
    Returns information about the currently active database backend.
    """
    return {
        "configured_url": settings.DATABASE_URL,
        "active_type": active_db_type,
        "is_sqlite_fallback": active_db_type == "sqlite" and settings.DATABASE_URL.startswith("postgresql"),
        "url_masked": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
    }
