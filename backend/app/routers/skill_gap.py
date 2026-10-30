import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.skill_gap import SkillGapAnalysisResponse
from app.services.skill_gap_service import analyze_skill_gap, get_latest_skill_gap_result

logger = logging.getLogger("app.routers.skill_gap")

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap Analysis"])


from app.models.student_profile import StudentProfile
from app.models.models import JobRole
from app.services.company_job_service import seed_sample_companies_and_jobs

def _get_or_run_default_analysis(db: Session, current_user: User) -> SkillGapAnalysisResponse:
    """Helper to return latest analysis or run for target job / first available job."""
    result = get_latest_skill_gap_result(db, current_user)
    if result:
        return result

    seed_sample_companies_and_jobs(db)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    job = None
    if profile and profile.target_job_role:
        job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()
    if not job:
        job = db.query(JobRole).first()

    if job:
        try:
            return analyze_skill_gap(db, current_user, job.id)
        except Exception as e:
            logger.warning(f"Could not auto-generate initial skill gap: {e}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No job roles available for skill gap analysis. Please select a target job."
    )


@router.post("/analyze/{job_role_id}", response_model=SkillGapAnalysisResponse)
def run_skill_gap_analysis(
    job_role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes Skill Gap Analysis between the authenticated student's profile & resume
    and the specified target job role. Stores results in the database.
    """
    try:
        result = analyze_skill_gap(db, current_user, job_role_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analyze", response_model=SkillGapAnalysisResponse)
@router.post("/analyze", response_model=SkillGapAnalysisResponse)
def run_default_skill_gap_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes or returns Skill Gap Analysis for the student's target job role.
    """
    return _get_or_run_default_analysis(db, current_user)


@router.get("", response_model=SkillGapAnalysisResponse)
@router.get("/", response_model=SkillGapAnalysisResponse)
@router.get("/latest", response_model=SkillGapAnalysisResponse)
def get_my_latest_skill_gap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the most recent skill gap evaluation for the authenticated student.
    Auto-initializes analysis if none exists yet.
    """
    return _get_or_run_default_analysis(db, current_user)


@router.get("/job/{job_role_id}", response_model=SkillGapAnalysisResponse)
def get_job_skill_gap(
    job_role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the existing or executes a fresh skill gap evaluation for a specific job role.
    """
    result = get_latest_skill_gap_result(db, current_user, job_role_id=job_role_id)
    if not result:
        # Run fresh analysis on demand
        try:
            result = analyze_skill_gap(db, current_user, job_role_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    return result
