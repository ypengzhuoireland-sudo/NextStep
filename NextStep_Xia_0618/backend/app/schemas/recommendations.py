from pydantic import BaseModel

from app.schemas.exercises import ExerciseDetail


class NextRecommendationRequest(BaseModel):
    session_id: str | None = None
    student_id: str | None = None
    current_exercise_id: str | None = None
    strategy: str = "adaptive"


class NextRecommendationResponse(BaseModel):
    exercise: ExerciseDetail | None
    reason: str
    strategy: str
    confidence: float
