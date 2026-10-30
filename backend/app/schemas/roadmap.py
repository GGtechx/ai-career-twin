from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class RoadmapItem(BaseModel):
    item_id: str
    stage: str  # "Skill Foundation", "Skill Development", "Project Development", "Certification", "Coding & Aptitude", "Interview Preparation", "Placement Ready"
    title: str
    description: str
    priority: str  # "High", "Medium", "Low"
    estimated_duration: str
    status: str  # "Not Started", "In Progress", "Completed"
    completion_percentage: float = 0.0

class RoadmapStage(BaseModel):
    stage_number: int
    stage_name: str
    description: str
    items: List[RoadmapItem]
    stage_progress_percentage: float

class CareerRoadmapResponse(BaseModel):
    id: int
    student_profile_id: int
    job_role_id: Optional[int] = None
    target_job_title: str
    target_company_name: str
    title: str
    target_timeline_weeks: int
    current_week: int
    overall_progress_percentage: float
    stages: List[RoadmapStage]
    total_tasks: int
    completed_tasks: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskProgressUpdateRequest(BaseModel):
    status: str  # "Not Started", "In Progress", "Completed"
    completion_percentage: Optional[float] = None
    notes: Optional[str] = None
