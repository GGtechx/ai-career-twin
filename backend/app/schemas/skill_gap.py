from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class SkillGapItem(BaseModel):
    skill: str
    priority: str  # "High Priority", "Medium Priority", "Low Priority"
    category: str  # "Must-Have", "Preferred"
    recommendation: str

class SkillGapAnalysisResponse(BaseModel):
    id: Optional[int] = None
    student_profile_id: int
    job_role_id: int
    job_title: str
    company_name: str
    match_percentage: float
    readiness_tier: str  # "High Readiness", "Moderate Readiness", "Low Readiness"
    matched_skills: List[str]
    missing_critical_skills: List[str]
    missing_secondary_skills: List[str]
    priority_skill_gaps: List[SkillGapItem]
    skill_strengths: List[str]
    recommended_skills: List[str]
    eligibility_status: Dict[str, Any]
    analysis_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SkillGapHistoryItem(BaseModel):
    id: int
    job_role_id: int
    job_title: str
    company_name: str
    match_percentage: float
    readiness_tier: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
