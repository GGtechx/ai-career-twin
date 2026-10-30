from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.profile import StudentProfileResponse, StudentProfileUpdate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/profile", tags=["Student Profile"])

def _format_profile_response(user: User, profile: StudentProfile) -> StudentProfileResponse:
    return StudentProfileResponse(
        id=profile.id,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        college_name=profile.college_name,
        degree=profile.degree,
        branch=profile.branch,
        cgpa=profile.cgpa or 0.0,
        college_tier=profile.college_tier,
        current_year=profile.current_year,
        current_semester=profile.current_semester,
        graduation_year=profile.graduation_year,
        roll_number=profile.roll_number,
        phone=profile.phone,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        technical_skills=profile.technical_skills or [],
        soft_skills=profile.soft_skills or [],
        programming_languages=profile.programming_languages or [],
        coding_score=profile.coding_score or 0.0,
        aptitude_score=profile.aptitude_score or 0.0,
        communication_score=profile.communication_score or 0.0,
        projects=profile.projects or [],
        certifications=profile.certifications or [],
        internships=profile.internships or [],
        interests=profile.interests or [],
        career_goal=profile.career_goal,
        target_company=profile.target_company,
        target_job_role=profile.target_job_role,
        bio=profile.bio,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        leetcode_url=profile.leetcode_url,
        portfolio_url=profile.portfolio_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.get("", response_model=StudentProfileResponse)
@router.get("/", response_model=StudentProfileResponse)
@router.get("/me", response_model=StudentProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the authenticated student's full profile.
    Protected by JWT Bearer token.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        # Create default profile if not exists
        profile = StudentProfile(
            user_id=current_user.id,
            college_name="Engineering College",
            degree="B.Tech",
            branch="CSE",
            cgpa=7.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return _format_profile_response(current_user, profile)

@router.put("", response_model=StudentProfileResponse)
@router.put("/", response_model=StudentProfileResponse)
@router.post("", response_model=StudentProfileResponse)
@router.post("/", response_model=StudentProfileResponse)
@router.put("/me", response_model=StudentProfileResponse)
def update_my_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the authenticated student's profile information.
    Protected by JWT Bearer token.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    # Update full_name on User model if provided
    if profile_in.full_name is not None and profile_in.full_name.strip():
        current_user.full_name = profile_in.full_name.strip()
        db.add(current_user)

    # Update profile fields if provided
    update_data = profile_in.model_dump(exclude_unset=True)
    update_data.pop("full_name", None)

    for field, value in update_data.items():
        if hasattr(profile, field):
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)

    # Automatic Career Twin recalculation hook
    from app.services.career_twin_service import on_profile_or_activity_updated
    on_profile_or_activity_updated(db, current_user, "Profile Skills & Info Updated")

    return _format_profile_response(current_user, profile)
