import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.dashboard import StudentDashboardResponse
from app.services.dashboard_service import get_student_dashboard_summary

logger = logging.getLogger("app.routers.dashboard")

router = APIRouter(prefix="/dashboard", tags=["Main Student Dashboard"])


@router.get("", response_model=StudentDashboardResponse)
@router.get("/", response_model=StudentDashboardResponse)
@router.get("/summary", response_model=StudentDashboardResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full unified dashboard overview for the authenticated student:
    Profile, Resume ATS score, Skills, Target Job, Skill Gaps, Placement Readiness,
    Roadmap Progress, Digital Career Twin, and Next Actions.
    """
    try:
        return get_student_dashboard_summary(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error compiling dashboard summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving student dashboard."
        )
