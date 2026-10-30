import os
import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Resume
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.resume import ResumeUploadResponse, ResumeAnalysisResponse, ResumeListResponse
from app.services.auth_service import get_current_user
from app.services.resume_analyzer import analyze_resume, compare_with_profile
from app.utils.text_extraction import extract_text_from_pdf_bytes, clean_text

logger = logging.getLogger("app.routers.resume")

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}

UPLOAD_DIR = "uploads/resumes"


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _get_profile(db: Session, user: User) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please complete your profile first."
        )
    return profile


def _extract_profile_data(profile: StudentProfile) -> Dict[str, Any]:
    return {
        "technical_skills": list(profile.technical_skills or []),
        "programming_languages": list(profile.programming_languages or []),
        "phone": profile.phone,
        "linkedin_url": profile.linkedin_url,
        "github_url": profile.github_url,
        "portfolio_url": profile.portfolio_url,
        "college_name": profile.college_name,
        "cgpa": profile.cgpa,
        "degree": profile.degree,
        "projects": list(profile.projects or []),
        "certifications": list(profile.certifications or []),
        "internships": list(profile.internships or []),
    }


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a PDF resume, extracts text, performs NLP analysis, and stores
    the results in the database. Returns the analysis summary.
    """
    # 1. Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Only .pdf files are supported."
        )

    # 2. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: '{file.content_type}'. Only PDF files are accepted."
        )

    file_bytes = await file.read()

    # 3. Check for empty file
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    # 4. Check file size limit
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
        )

    # 5. Get student profile for comparison
    profile = _get_profile(db, current_user)
    profile_data = _extract_profile_data(profile)

    # 6. Text extraction
    try:
        raw_text, extraction_method = extract_text_from_pdf_bytes(file_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    cleaned = clean_text(raw_text)

    if len(cleaned.split()) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The PDF appears to contain very little text (possibly image-based, encrypted, or empty). Please upload a standard text-based PDF."
        )

    # 7. NLP Analysis
    analysis = analyze_resume(
        cleaned_text=cleaned,
        profile_data=profile_data,
    )

    # 8. Save file to disk safely
    _ensure_upload_dir()
    safe_name = f"user_{current_user.id}_{os.path.basename(file.filename or 'resume.pdf')}"
    safe_name = safe_name.replace(" ", "_").replace("..", "")
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # 9. Build extracted payload for DB JSON column
    extracted_skills_payload = {
        "technical_skills": analysis["technical_skills"],
        "programming_languages": analysis["programming_languages"],
        "soft_skills": analysis["soft_skills"],
        "education": analysis["education"],
        "projects": analysis["projects"],
        "certifications": analysis["certifications"],
        "internships": analysis["internships"],
        "experience": analysis["experience"],
        "extracted_experience_years": analysis["extracted_experience_years"],
        "contact": {
            "name": analysis["name"],
            "email": analysis["email"],
            "phone": analysis["phone"],
            "linkedin_url": analysis["linkedin_url"],
            "github_url": analysis["github_url"],
            "portfolio_url": analysis["portfolio_url"],
        },
        "profile_comparison": analysis["profile_comparison"],
        "missing_profile_info": analysis["missing_profile_info"],
        "ats_breakdown": analysis["ats_breakdown"],
        "sections_detected": analysis["sections_detected"],
        "word_count": analysis["word_count"],
        "ats_rating": analysis["ats_rating"],
        "extraction_method": extraction_method,
    }

    # 10. Upsert resume record in DB
    existing = db.query(Resume).filter(
        Resume.student_profile_id == profile.id,
        Resume.file_name == file.filename
    ).first()

    if existing:
        existing.file_path = file_path
        existing.file_size_bytes = len(file_bytes)
        existing.parsed_text = cleaned[:10000]
        existing.ats_score = analysis["ats_score"]
        existing.extracted_skills = extracted_skills_payload
        existing.extracted_experience_years = float(analysis["extracted_experience_years"])
        existing.formatting_score = analysis["ats_score"]
        existing.strengths = analysis["strengths"]
        existing.improvements_suggested = analysis["improvements_suggested"]
        resume_record = existing
    else:
        resume_record = Resume(
            student_profile_id=profile.id,
            file_name=file.filename or "resume.pdf",
            file_path=file_path,
            file_size_bytes=len(file_bytes),
            parsed_text=cleaned[:10000],
            ats_score=analysis["ats_score"],
            extracted_skills=extracted_skills_payload,
            extracted_experience_years=float(analysis["extracted_experience_years"]),
            formatting_score=analysis["ats_score"],
            strengths=analysis["strengths"],
            improvements_suggested=analysis["improvements_suggested"],
        )
        db.add(resume_record)

    db.commit()
    db.refresh(resume_record)

    return ResumeUploadResponse(
        id=resume_record.id,
        file_name=resume_record.file_name,
        file_size_bytes=resume_record.file_size_bytes,
        ats_score=resume_record.ats_score,
        ats_rating=analysis["ats_rating"],
        extracted_skills=resume_record.extracted_skills,
        improvements_suggested=resume_record.improvements_suggested,
        strengths=resume_record.strengths,
        skills_to_add_to_profile=analysis["skills_to_add_to_profile"],
        skills_missing_from_resume=analysis["skills_missing_from_resume"],
        missing_profile_info=analysis["missing_profile_info"],
        uploaded_at=resume_record.uploaded_at,
    )


@router.get("", response_model=ResumeListResponse)
@router.get("/", response_model=ResumeListResponse)
@router.get("/my-resume", response_model=ResumeListResponse)
def get_my_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns metadata for the most recently uploaded resume.
    """
    profile = _get_profile(db, current_user)
    resume = db.query(Resume)\
        .filter(Resume.student_profile_id == profile.id)\
        .order_by(Resume.uploaded_at.desc())\
        .first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload your resume first."
        )

    skills_data = resume.extracted_skills or {}

    return ResumeListResponse(
        id=resume.id,
        file_name=resume.file_name,
        file_size_bytes=resume.file_size_bytes,
        ats_score=resume.ats_score,
        ats_rating=skills_data.get("ats_rating", "Fair"),
        uploaded_at=resume.uploaded_at,
    )


@router.get("/analysis", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the full NLP analysis of the latest uploaded resume.
    Includes skill extraction, ATS breakdown, and dynamic profile comparison.
    """
    profile = _get_profile(db, current_user)
    resume = db.query(Resume)\
        .filter(Resume.student_profile_id == profile.id)\
        .order_by(Resume.uploaded_at.desc())\
        .first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume uploaded. Please upload your PDF resume first."
        )

    skills_data = resume.extracted_skills or {}
    contact_data = skills_data.get("contact", {})

    # Re-evaluate profile comparison against current profile state
    profile_data = _extract_profile_data(profile)
    dynamic_comparison = compare_with_profile(
        resume_technical_skills=skills_data.get("technical_skills", []),
        resume_prog_languages=skills_data.get("programming_languages", []),
        profile_data={
            **profile_data,
            "resume_has_github": bool(contact_data.get("github_url")),
            "resume_has_linkedin": bool(contact_data.get("linkedin_url")),
            "resume_has_portfolio": bool(contact_data.get("portfolio_url")),
            "resume_has_phone": bool(contact_data.get("phone")),
            "resume_projects": skills_data.get("projects", []),
            "resume_certs": skills_data.get("certifications", []),
            "resume_internships": skills_data.get("internships", []),
        }
    )

    return ResumeAnalysisResponse(
        id=resume.id,
        file_name=resume.file_name,
        file_size_bytes=resume.file_size_bytes,
        ats_score=resume.ats_score,
        ats_rating=skills_data.get("ats_rating", "Fair"),
        word_count=skills_data.get("word_count"),
        extracted_name=contact_data.get("name"),
        extracted_email=contact_data.get("email"),
        extracted_phone=contact_data.get("phone"),
        extracted_linkedin=contact_data.get("linkedin_url"),
        extracted_github=contact_data.get("github_url"),
        extracted_portfolio=contact_data.get("portfolio_url"),
        education=skills_data.get("education", []),
        technical_skills=skills_data.get("technical_skills", []),
        programming_languages=skills_data.get("programming_languages", []),
        soft_skills=skills_data.get("soft_skills", []),
        projects=skills_data.get("projects", []),
        certifications=skills_data.get("certifications", []),
        internships=skills_data.get("internships", []),
        experience=skills_data.get("experience", []),
        extracted_experience_years=resume.extracted_experience_years or 0.0,
        ats_breakdown=skills_data.get("ats_breakdown", {}),
        strengths=resume.strengths or [],
        improvements_suggested=resume.improvements_suggested or [],
        skills_to_add_to_profile=dynamic_comparison["skills_to_add_to_profile"],
        skills_missing_from_resume=dynamic_comparison["skills_missing_from_resume"],
        missing_profile_info=dynamic_comparison["missing_profile_info"],
        sections_detected=skills_data.get("sections_detected", []),
        uploaded_at=resume.uploaded_at,
    )
