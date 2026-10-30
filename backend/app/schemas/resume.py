from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResumeUploadResponse(BaseModel):
    id: int
    file_name: str
    file_size_bytes: Optional[int] = None
    ats_score: float
    ats_rating: str
    extracted_skills: Optional[Dict[str, Any]] = None
    improvements_suggested: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    skills_to_add_to_profile: Optional[List[str]] = None
    skills_missing_from_resume: Optional[List[str]] = None
    missing_profile_info: Optional[List[str]] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeAnalysisResponse(BaseModel):
    id: int
    file_name: str
    file_size_bytes: Optional[int] = None
    ats_score: float
    ats_rating: str
    word_count: Optional[int] = None

    # Extracted contact
    extracted_name: Optional[str] = None
    extracted_email: Optional[str] = None
    extracted_phone: Optional[str] = None
    extracted_linkedin: Optional[str] = None
    extracted_github: Optional[str] = None
    extracted_portfolio: Optional[str] = None

    # Extracted structured data
    education: Optional[List[Dict[str, Any]]] = None
    technical_skills: Optional[List[str]] = None
    programming_languages: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    internships: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    extracted_experience_years: Optional[float] = 0.0

    # Quality metrics
    ats_breakdown: Optional[Dict[str, Any]] = None
    strengths: Optional[List[str]] = None
    improvements_suggested: Optional[List[str]] = None

    # Profile comparison
    skills_to_add_to_profile: Optional[List[str]] = None
    skills_missing_from_resume: Optional[List[str]] = None
    missing_profile_info: Optional[List[str]] = None

    # Metadata
    sections_detected: Optional[List[str]] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeListResponse(BaseModel):
    id: int
    file_name: str
    file_size_bytes: Optional[int] = None
    ats_score: float
    ats_rating: Optional[str] = "Fair"
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
