from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardProfileSummary(BaseModel):
    user_id: int
    full_name: str
    email: str
    college_name: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    technical_skills: List[str] = []
    projects_count: int = 0
    certifications_count: int = 0
    internships_count: int = 0
    coding_score: float = 65.0
    aptitude_score: float = 65.0


class DashboardResumeSummary(BaseModel):
    has_resume: bool = False
    file_name: Optional[str] = None
    ats_score: Optional[float] = None
    ats_rating: Optional[str] = None
    extracted_skills_count: int = 0
    uploaded_at: Optional[datetime] = None


class DashboardTargetJobSummary(BaseModel):
    has_target: bool = False
    target_company: Optional[str] = None
    target_job_role: Optional[str] = None
    target_job_id: Optional[int] = None
    tier: Optional[str] = None


class DashboardSkillGapSummary(BaseModel):
    has_analysis: bool = False
    match_percentage: float = 0.0
    readiness_tier: str = "Moderate"
    matched_skills_count: int = 0
    missing_critical_skills: List[str] = []
    missing_secondary_skills: List[str] = []


class DashboardPlacementSummary(BaseModel):
    has_prediction: bool = False
    readiness_score: float = 65.0
    readiness_category: str = "Moderate Readiness"
    predicted_status: str = "Placed"
    placement_probability: float = 0.65
    predicted_salary_min_lpa: Optional[float] = 7.5
    predicted_salary_max_lpa: Optional[float] = 12.0
    top_strengths: List[str] = []
    top_risk_factors: List[str] = []


class DashboardRoadmapSummary(BaseModel):
    has_roadmap: bool = False
    current_stage: str = "Skill Foundation"
    overall_progress_percentage: float = 0.0
    completed_milestones: int = 0
    total_milestones: int = 4
    total_tasks: int = 14
    completed_tasks: int = 0


class DashboardTwinSummary(BaseModel):
    has_twin: bool = False
    twin_name: str = "Career Twin Alpha"
    twin_version: int = 1
    overall_twin_score: float = 64.0
    benchmark_percentile: float = 50.0
    projected_salary_lpa: float = 7.5
    radar_breakdown: Dict[str, float] = {}


class DashboardActionItem(BaseModel):
    id: Optional[int] = None
    title: str
    category: str
    priority: str
    action_url: Optional[str] = None


class StudentDashboardResponse(BaseModel):
    profile: DashboardProfileSummary
    resume: DashboardResumeSummary
    target_job: DashboardTargetJobSummary
    skill_gap: DashboardSkillGapSummary
    placement: DashboardPlacementSummary
    roadmap: DashboardRoadmapSummary
    career_twin: DashboardTwinSummary
    top_action_items: List[DashboardActionItem] = []
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
