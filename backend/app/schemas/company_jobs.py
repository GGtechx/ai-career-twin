from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    tier: Optional[str] = "Tier 1"
    website: Optional[str] = None
    logo_url: Optional[str] = None
    hiring_status: Optional[str] = "Active"
    description: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    active_jobs_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class JobRequirementResponse(BaseModel):
    id: int
    job_role_id: int
    min_cgpa: float
    max_active_backlogs: int
    eligible_branches: Optional[List[str]] = None
    must_have_skills: List[str]
    good_to_have_skills: Optional[List[str]] = None
    min_internships_count: int
    min_projects_count: int

    model_config = ConfigDict(from_attributes=True)

class JobRoleBase(BaseModel):
    title: str
    domain: str
    role_type: str = "Full-Time"
    experience_level: str = "Entry-Level"
    package_min_lpa: Optional[float] = None
    package_max_lpa: Optional[float] = None
    location: str = "Bengaluru / Hybrid"
    description: Optional[str] = None
    is_active: bool = True

class JobRoleResponse(JobRoleBase):
    id: int
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    company_tier: Optional[str] = None
    company_logo_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobRoleDetailResponse(JobRoleResponse):
    requirement: Optional[JobRequirementResponse] = None

    model_config = ConfigDict(from_attributes=True)

class TargetJobSelectResponse(BaseModel):
    student_profile_id: int
    target_job_role_id: int
    target_job_title: str
    target_company_name: str
    message: str

class CareerTargetUpdateRequest(BaseModel):
    job_id: Optional[int] = None
    company_id: Optional[int] = None
    role_id: Optional[int] = None

class CareerTargetResponse(BaseModel):
    id: Optional[int] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    company_tier: Optional[str] = None
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    title: Optional[str] = None
    domain: Optional[str] = None
    role_type: Optional[str] = "Full-Time"
    experience_level: Optional[str] = "Entry-Level"
    package_min_lpa: Optional[float] = None
    package_max_lpa: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None
    required_skills: List[str] = []
    requirements: Optional[Dict[str, Any]] = None
    requirement: Optional[Dict[str, Any]] = None
    experience_requirements: Optional[str] = None
    preferred_skills: List[str] = []
    student_profile_id: Optional[int] = None
    target_job_role_id: Optional[int] = None
    target_job_title: Optional[str] = None
    target_company_name: Optional[str] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")

