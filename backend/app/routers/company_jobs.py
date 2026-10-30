import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.services.auth_service import get_current_user
from app.schemas.company_jobs import (
    CompanyResponse,
    JobRoleResponse,
    JobRoleDetailResponse,
    JobRequirementResponse,
    TargetJobSelectResponse,
    CareerTargetResponse,
    CareerTargetUpdateRequest
)
from app.services.company_job_service import (
    list_companies,
    get_company_detail,
    list_job_roles,
    get_job_role_with_requirements,
    set_student_target_job,
    get_student_career_target,
    seed_sample_companies_and_jobs
)

logger = logging.getLogger("app.routers.company_jobs")

router = APIRouter(tags=["Companies & Job Requirements"])


@router.get("/companies", response_model=List[CompanyResponse])
def get_companies(
    search: Optional[str] = Query(None, description="Search companies by name or industry"),
    db: Session = Depends(get_db)
):
    """
    List all companies. Automatically seeds sample development data if empty.
    """
    # Ensure sample data is present
    seed_sample_companies_and_jobs(db)
    return list_companies(db, search=search)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get single company by ID."""
    company = get_company_detail(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )
    return company


@router.get("/jobs", response_model=List[JobRoleResponse])
def get_jobs(
    company_id: Optional[int] = Query(None, description="Filter jobs by company ID"),
    domain: Optional[str] = Query(None, description="Filter jobs by tech domain"),
    db: Session = Depends(get_db)
):
    """List active job roles with optional company and domain filtering."""
    seed_sample_companies_and_jobs(db)
    return list_job_roles(db, company_id=company_id, domain=domain)


@router.get("/jobs/my-target", response_model=Optional[CareerTargetResponse])
@router.get("/career-target", response_model=Optional[CareerTargetResponse])
def get_my_target_job(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the authenticated student's selected target job and full requirements.
    Acts as the single source of truth for active career target.
    """
    target = get_student_career_target(db, current_user)
    return target


@router.get("/jobs/{job_id}", response_model=JobRoleDetailResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get job role detail with requirements."""
    seed_sample_companies_and_jobs(db)
    job_detail = get_job_role_with_requirements(db, job_id)
    if not job_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job role with ID {job_id} not found."
        )
    return job_detail


@router.get("/jobs/{job_id}/requirements", response_model=JobRequirementResponse)
def get_job_requirements(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get complete requirements for a selected job."""
    seed_sample_companies_and_jobs(db)
    job_detail = get_job_role_with_requirements(db, job_id)
    if not job_detail or not job_detail.get("requirement"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirements for job role ID {job_id} not found."
        )
    return job_detail["requirement"]


@router.post("/jobs/{job_id}/select-target", response_model=CareerTargetResponse)
def select_target_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Selects a target job role for the authenticated student.
    Persists target_company and target_job_role in student_profile.
    Immediately synchronizes Skill Gap, Recommendations, Roadmap, and Career Twin.
    """
    seed_sample_companies_and_jobs(db)
    try:
        result = set_student_target_job(db, current_user, job_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/career-target", response_model=CareerTargetResponse)
@router.post("/career-target", response_model=CareerTargetResponse)
@router.post("/jobs/select-target", response_model=CareerTargetResponse)
def select_target_job_body(
    payload: Optional[CareerTargetUpdateRequest] = None,
    job_id: Optional[int] = Query(None),
    company_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unified endpoint for setting global active career target."""
    target_id = job_id
    if target_id is None and payload:
        target_id = payload.job_id or payload.role_id
    if target_id is None and payload and payload.company_id:
        from app.models.models import JobRole
        j = db.query(JobRole).filter(JobRole.company_id == payload.company_id).first()
        if j:
            target_id = j.id
    if target_id is None and company_id:
        from app.models.models import JobRole
        j = db.query(JobRole).filter(JobRole.company_id == company_id).first()
        if j:
            target_id = j.id

    if target_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="job_id is required.")
    return select_target_job(target_id, current_user, db)


@router.post("/companies/seed")
def trigger_seed_companies(db: Session = Depends(get_db)):
    """Manually triggers seeding of 10 companies and 15 job roles."""
    result = seed_sample_companies_and_jobs(db)
    return {
        "status": "success",
        "message": "Sample development data ensured in database.",
        "counts": result
    }
