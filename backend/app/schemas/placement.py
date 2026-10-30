from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class PlacementPredictionResponse(BaseModel):
    id: Optional[int] = None
    student_profile_id: int
    readiness_score: float  # 0 to 100
    predicted_status: str  # "Placed" or "Not Placed"
    placement_probability: float  # e.g., 0.82
    readiness_category: str  # "Placement Ready (High)", "Moderate Readiness", "At Risk"
    predicted_salary_min_lpa: Optional[float] = None
    predicted_salary_max_lpa: Optional[float] = None
    confidence_score: float
    strengths: List[str]
    weak_areas: List[str]
    improvement_suggestions: List[str]
    feature_breakdown: Dict[str, Any]
    model_version: str = "v1.0-basepaper"
    assessed_at: datetime

    model_config = ConfigDict(from_attributes=True)
