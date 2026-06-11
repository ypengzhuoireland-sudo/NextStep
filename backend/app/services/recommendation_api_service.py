from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.schemas.recommendations import (
    NextRecommendationRequest,
    NextRecommendationResponse,
)
from app.services.exercise_service import DEFAULT_STUDENT_ID, get_exercise_by_id


def build_next_recommendation(
    db: Session,
    request: NextRecommendationRequest,
) -> NextRecommendationResponse:
    student_id = request.student_id or DEFAULT_STUDENT_ID
    weakest = db.scalars(
        select(StudentMastery)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.mastery, StudentMastery.kc_id)
    ).first()

    if weakest is None:
        exercise_id = db.scalars(select(Exercise.id).order_by(Exercise.id)).first()
        exercise = None if exercise_id is None else get_exercise_by_id(db, exercise_id, student_id)

        return NextRecommendationResponse(
            exercise=exercise,
            reason="Recommended the first available exercise because no mastery profile exists yet.",
            strategy=request.strategy,
            confidence=0.5,
        )

    exercise_id = db.scalars(
        select(Exercise.id)
        .join(ExerciseKnowledgeComponent, ExerciseKnowledgeComponent.exercise_id == Exercise.id)
        .where(ExerciseKnowledgeComponent.kc_id == weakest.kc_id)
        .order_by(Exercise.id)
    ).first()
    exercise = None if exercise_id is None else get_exercise_by_id(db, exercise_id, student_id)

    return NextRecommendationResponse(
        exercise=exercise,
        reason=(
            f"Recommended because {weakest.kc_id} mastery is "
            f"{weakest.mastery:.2f} below the target threshold."
        ),
        strategy="lowest_mastery_with_difficulty_match",
        confidence=0.82,
    )
