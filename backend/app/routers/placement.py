import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.placement import PlacementPredictionResponse
from app.services.placement_service import predict_placement_readiness, get_latest_placement_readiness

logger = logging.getLogger("app.routers.placement")

router = APIRouter(prefix="/placement", tags=["Placement Readiness Prediction"])


@router.post("", response_model=PlacementPredictionResponse)
@router.post("/", response_model=PlacementPredictionResponse)
@router.post("/predict", response_model=PlacementPredictionResponse)
def run_placement_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Runs placement readiness inference for the authenticated student using their
    live database attributes (CGPA, coding score, aptitude, projects, internships, backlogs).
    Does NOT reload the large base-paper CSV on inference.
    """
    try:
        result = predict_placement_readiness(db, current_user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PlacementPredictionResponse)
@router.get("/", response_model=PlacementPredictionResponse)
@router.get("/latest", response_model=PlacementPredictionResponse)
def get_my_placement_readiness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the latest placement readiness assessment for the student.
    If none exists, executes a fresh prediction automatically.
    """
    result = get_latest_placement_readiness(db, current_user)
    if not result:
        try:
            result = predict_placement_readiness(db, current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    return result
