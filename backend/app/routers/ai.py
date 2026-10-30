import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.ai import (
    CareerAssistantRequest, CareerAssistantResponse,
    LLMPersonalizedRecommendationResponse
)
from app.services.rag_service import (
    answer_career_question,
    generate_llm_personalized_recommendations
)
from app.services.vector_store import vector_store

logger = logging.getLogger("app.routers.ai")

router = APIRouter(prefix="/ai", tags=["AI Intelligence Layer"])


@router.post("/career-assistant", response_model=CareerAssistantResponse)
def ask_career_assistant(
    payload: CareerAssistantRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG-powered Career Assistant.
    Retrieves grounded career knowledge chunks and synthesizes a personalized answer
    using the student's live profile, resume, skill gaps, and roadmap context.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question string cannot be empty."
        )

    try:
        return answer_career_question(
            db,
            current_user,
            question=payload.question.strip(),
            chat_history=payload.chat_history
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in career assistant: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating career assistant response."
        )


@router.get("/recommendations", response_model=LLMPersonalizedRecommendationResponse)
@router.post("/recommendations", response_model=LLMPersonalizedRecommendationResponse)
def get_personalized_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Synthesizes narrative LLM personalized career recommendations explaining
    deterministic skill gaps, placement readiness, and project goals without altering scores.
    """
    try:
        return generate_llm_personalized_recommendations(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating personalized LLM recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating personalized recommendations."
        )


@router.get("/knowledge-base/search")
def search_knowledge_base(
    query: str = Query(..., description="Semantic search query"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    top_k: int = Query(4, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """
    Direct semantic search over internal career knowledge base vectors using FAISS.
    """
    results = vector_store.search(query=query, top_k=top_k, category=category)
    return {
        "query": query,
        "results_count": len(results),
        "results": results
    }
