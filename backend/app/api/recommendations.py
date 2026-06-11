from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendations import (
    NextRecommendationRequest,
    NextRecommendationResponse,
)
from app.services.recommendation_api_service import build_next_recommendation

router = APIRouter()


@router.post("/recommendations/next", response_model=NextRecommendationResponse)
def get_next_recommendation(
    request: NextRecommendationRequest,
    db: Session = Depends(get_db),
) -> NextRecommendationResponse:
    return build_next_recommendation(db, request)
