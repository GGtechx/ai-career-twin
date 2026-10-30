import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.roadmap import CareerRoadmapResponse, TaskProgressUpdateRequest
from app.services.roadmap_service import (
    generate_career_roadmap,
    get_student_career_roadmap,
    update_task_progress
)

logger = logging.getLogger("app.routers.roadmap")

router = APIRouter(prefix="/roadmap", tags=["Personalized Career Roadmap"])


@router.get("", response_model=CareerRoadmapResponse)
def get_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the 7-stage personalized career roadmap for the student.
    Automatically generates one if not yet active.
    """
    try:
        return get_student_career_roadmap(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/generate", response_model=CareerRoadmapResponse)
def trigger_generate_roadmap(
    force_refresh: bool = Query(False, description="Re-generate fresh 7-stage roadmap"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a personalized 7-stage roadmap aligned with the student's target job,
    skill gaps, placement readiness, and recommendations.
    """
    try:
        return generate_career_roadmap(db, current_user, force_refresh=force_refresh)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/tasks/{task_id}", response_model=CareerRoadmapResponse)
def update_roadmap_task(
    task_id: str,
    payload: TaskProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates status and completion percentage of a specific task item in the roadmap.
    Logs progress into the progress_tracking database table.
    """
    try:
        res = update_task_progress(
            db,
            current_user,
            item_id=task_id,
            status=payload.status,
            completion_percentage=payload.completion_percentage,
            notes=payload.notes
        )
        if payload.status == "Completed":
            from app.services.career_twin_service import on_profile_or_activity_updated
            on_profile_or_activity_updated(db, current_user, f"Roadmap Task Completed: {task_id}")
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
