from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class DigitalCareerTwinResponse(BaseModel):
    id: int
    student_profile_id: int
    twin_name: str
    twin_version: int
    coding_score: float
    aptitude_score: float
    communication_score: float
    logical_score: float
    leadership_score: float
    project_score: float
    overall_twin_score: float
    benchmark_percentile: float
    projected_placement_chance: float
    projected_salary_lpa: float
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    skill_match_percentage: float = 0.0
    placement_readiness_score: float = 0.0
    current_roadmap_stage: str = "Skill Foundation"
    roadmap_progress_percentage: float = 0.0
    radar_breakdown: Dict[str, float]
    timeline: List[Dict[str, Any]]
    last_simulated_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WhatIfSimulationRequest(BaseModel):
    added_skills: List[str] = []
    added_projects_count: int = 0
    added_certifications: List[str] = []
    coding_score_delta: float = 0.0
    aptitude_score_delta: float = 0.0
    added_internships_count: int = 0


class SimulationMetrics(BaseModel):
    skill_match_percentage: float
    placement_readiness_score: float
    projected_placement_chance: float
    projected_salary_lpa: float
    overall_twin_score: float


class SimulationDeltas(BaseModel):
    match_percentage_delta: float
    placement_readiness_delta: float
    placement_chance_delta: float
    salary_delta_lpa: float
    twin_score_delta: float


class WhatIfSimulationResponse(BaseModel):
    is_simulation: bool = True
    disclaimer: str = "Simulation results are predictive estimates. They do not alter your permanent career profile."
    baseline: SimulationMetrics
    simulated: SimulationMetrics
    deltas: SimulationDeltas
    resolved_skills: List[str]
    remaining_skill_gaps: List[str]
    analysis_summary: str
    simulated_at: datetime
