import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.twin import (
    DigitalCareerTwinResponse, WhatIfSimulationRequest, WhatIfSimulationResponse
)
from app.services.career_twin_service import (
    sync_career_twin, simulate_what_if_career_state
)

logger = logging.getLogger("app.routers.twin")

router = APIRouter(prefix="/twin", tags=["Digital Career Twin"])


@router.get("", response_model=DigitalCareerTwinResponse)
@router.get("/", response_model=DigitalCareerTwinResponse)
@router.get("/state", response_model=DigitalCareerTwinResponse)
def get_career_twin_state(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the authenticated student's current Digital Career Twin state.
    Automatically synchronizes if needed.
    """
    try:
        return sync_career_twin(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching Career Twin state: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving Digital Career Twin."
        )


@router.post("/sync", response_model=DigitalCareerTwinResponse)
def trigger_sync_twin(
    event_label: Optional[str] = Query("Manual Sync", description="Reason for sync event"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Explicitly triggers recalculation of Career Twin scores, percentiles, and timeline history.
    """
    try:
        return sync_career_twin(db, current_user, trigger_event=event_label)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error syncing Career Twin: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error synchronizing Digital Career Twin."
        )


@router.post("/what-if", response_model=WhatIfSimulationResponse)
@router.post("/simulate", response_model=WhatIfSimulationResponse)
def run_what_if_simulation(
    payload: WhatIfSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    What-If Career Simulation.
    Simulates projected changes to skill match, placement readiness, and career twin score
    without altering permanent student profile data.
    """
    try:
        return simulate_what_if_career_state(db, current_user, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error running What-If simulation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating simulation outcome."
        )
