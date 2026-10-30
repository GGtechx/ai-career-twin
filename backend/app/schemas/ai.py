from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class CareerAssistantRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None


class RetrievedKnowledgeChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    category: str
    tags: List[str] = []
    content: str
    similarity_score: float


class StudentCareerContext(BaseModel):
    student_name: str
    degree: str
    branch: str
    cgpa: float
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    skill_match_percentage: Optional[float] = None
    readiness_category: Optional[str] = None
    placement_readiness_score: Optional[float] = None
    top_missing_skills: List[str] = []
    current_roadmap_stage: Optional[str] = None


class CareerAssistantResponse(BaseModel):
    question: str
    answer: str
    retrieved_sources: List[RetrievedKnowledgeChunk]
    student_context: StudentCareerContext
    suggested_followups: List[str]
    is_fallback: bool = False
    generated_at: datetime


class NextSkillRecommendation(BaseModel):
    skill: str
    priority: str
    why_it_matters: str
    learning_path: str


class ProjectRecommendation(BaseModel):
    title: str
    description: str
    tech_stack: List[str]
    target_impact: str


class LearningPriorityItem(BaseModel):
    area: str
    timeline: str
    rationale: str


class InterviewPrepGuide(BaseModel):
    technical_drills: List[str]
    system_design_or_architecture: str
    behavioral_focus: str


class LLMPersonalizedRecommendationResponse(BaseModel):
    student_profile_id: int
    target_role: str
    target_company: str
    deterministic_skill_match: float
    deterministic_placement_score: float
    next_skill_to_learn: NextSkillRecommendation
    recommended_project: ProjectRecommendation
    learning_priorities: List[LearningPriorityItem]
    interview_preparation: InterviewPrepGuide
    improvement_suggestions: List[str]
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
