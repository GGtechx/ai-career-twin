import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, active_db_type
from app.api.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.resume import router as resume_router
from app.routers.company_jobs import router as company_jobs_router
from app.routers.skill_gap import router as skill_gap_router
from app.routers.placement import router as placement_router
from app.routers.recommendation import router as recommendation_router
from app.routers.roadmap import router as roadmap_router
from app.routers.ai import router as ai_router
from app.routers.twin import router as twin_router
from app.routers.dashboard import router as dashboard_router

# Import all models to ensure they are registered with Base.metadata
import app.models  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager:
    Initializes database tables on startup and handles clean shutdown.
    """
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully! Backend type: {active_db_type}")
        logger.info(f"Total tables registered in metadata: {len(Base.metadata.tables)}")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API service for AI Digital Career Twin platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware for React + Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers - Support root prefix, /api prefix, and API v1 prefix (/api/v1/...)
app.include_router(health_router)
app.include_router(health_router, prefix="/api")
app.include_router(health_router, prefix="/api/v1")

app.include_router(auth_router)
app.include_router(auth_router, prefix="/api")
app.include_router(auth_router, prefix="/api/v1")

app.include_router(profile_router)
app.include_router(profile_router, prefix="/api")
app.include_router(profile_router, prefix="/api/v1")

app.include_router(resume_router)
app.include_router(resume_router, prefix="/api")
app.include_router(resume_router, prefix="/api/v1")

app.include_router(company_jobs_router)
app.include_router(company_jobs_router, prefix="/api")
app.include_router(company_jobs_router, prefix="/api/v1")

app.include_router(skill_gap_router)
app.include_router(skill_gap_router, prefix="/api")
app.include_router(skill_gap_router, prefix="/api/v1")

app.include_router(placement_router)
app.include_router(placement_router, prefix="/api")
app.include_router(placement_router, prefix="/api/v1")

app.include_router(recommendation_router)
app.include_router(recommendation_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api/v1")

app.include_router(roadmap_router)
app.include_router(roadmap_router, prefix="/api")
app.include_router(roadmap_router, prefix="/api/v1")

app.include_router(ai_router)
app.include_router(ai_router, prefix="/api")
app.include_router(ai_router, prefix="/api/v1")

app.include_router(twin_router)
app.include_router(twin_router, prefix="/api")
app.include_router(twin_router, prefix="/api/v1")

app.include_router(dashboard_router)
app.include_router(dashboard_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "database_info": f"{settings.API_V1_PREFIX}/health/db"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
