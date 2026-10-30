from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class RecommendationItemResponse(BaseModel):
    id: Optional[int] = None
    type: str  # "skill", "course", "project", "certification", "coding", "aptitude", "interview"
    title: str
    description: Optional[str] = None
    priority: str  # "High", "Medium", "Low"
    action_url: Optional[str] = None
    course_id: Optional[int] = None
    course_provider: Optional[str] = None
    mapped_skills: Optional[List[str]] = None
    estimated_effort_hours: Optional[float] = None
    relevance_score: float = 0.0  # 0 to 100 recommendation scoring
    is_completed: bool = False
    is_dismissed: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategorizedRecommendationsResponse(BaseModel):
    student_profile_id: int
    target_job_title: Optional[str] = None
    target_company_name: Optional[str] = None
    total_recommendations: int
    by_category: Dict[str, List[RecommendationItemResponse]]
    high_priority_count: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
