import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.recommendation import CategorizedRecommendationsResponse, RecommendationItemResponse
from app.services.recommendation_service import (
    generate_personalized_recommendations,
    get_student_recommendations,
    update_recommendation_status
)

logger = logging.getLogger("app.routers.recommendation")

router = APIRouter(prefix="/recommendations", tags=["Personalized Career Recommendations"])


@router.post("/generate", response_model=CategorizedRecommendationsResponse)
def trigger_generate_recommendations(
    force_refresh: bool = Query(False, description="Re-generate fresh recommendations"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates personalized recommendations for skills, courses, projects,
    certifications, coding practice, aptitude, and interview preparation.
    """
    try:
        return generate_personalized_recommendations(db, current_user, force_refresh=force_refresh)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=CategorizedRecommendationsResponse)
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves categorized recommendations for the authenticated student.
    """
    try:
        return get_student_recommendations(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{rec_id}/complete")
def toggle_recommendation_completion(
    rec_id: int,
    completed: bool = Query(True, description="True to mark completed, False to mark incomplete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks a recommendation task as completed or incomplete."""
    try:
        return update_recommendation_status(db, current_user, rec_id, is_completed=completed)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{rec_id}/dismiss")
def dismiss_recommendation(
    rec_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismisses a recommendation from the active view."""
    try:
        return update_recommendation_status(db, current_user, rec_id, is_dismissed=True)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
