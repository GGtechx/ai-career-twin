from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class StudentProfileBase(BaseModel):
    # Demographics & Academic
    college_name: Optional[str] = None
    degree: Optional[str] = "B.Tech"
    branch: Optional[str] = "CSE"
    cgpa: float = Field(default=0.0, ge=0.0, le=10.0)
    college_tier: Optional[str] = "Tier 2"
    current_year: Optional[int] = 3
    current_semester: Optional[int] = 6
    graduation_year: Optional[int] = None
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    # Skills Lists
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)

    # Assessments & Scores
    coding_score: float = Field(default=0.0, ge=0.0, le=100.0)
    aptitude_score: float = Field(default=0.0, ge=0.0, le=100.0)
    communication_score: float = Field(default=0.0, ge=0.0, le=100.0)

    # Portfolio & Experience
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    internships: List[Dict[str, Any]] = Field(default_factory=list)

    # Vision & Goals
    interests: List[str] = Field(default_factory=list)
    career_goal: Optional[str] = None
    target_company: Optional[str] = None
    target_job_role: Optional[str] = None

    # Links
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileUpdate(BaseModel):
    # Allow partial updates
    full_name: Optional[str] = None
    college_name: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    college_tier: Optional[str] = None
    current_year: Optional[int] = None
    current_semester: Optional[int] = None
    graduation_year: Optional[int] = None
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    programming_languages: Optional[List[str]] = None

    coding_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    aptitude_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    communication_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)

    projects: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    internships: Optional[List[Dict[str, Any]]] = None

    interests: Optional[List[str]] = None
    career_goal: Optional[str] = None
    target_company: Optional[str] = None
    target_job_role: Optional[str] = None

    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    full_name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
