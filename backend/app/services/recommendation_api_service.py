from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.schemas.recommendations import (
    NextRecommendationRequest,
    NextRecommendationResponse,
)
from app.services.ai.llm_client import (
    LLMGenerationError,
    OpenAIRecommendationExplanationService,
    create_fallback_explanation,
)
from app.services.ai.schemas import (
    CurrentExercise,
    RecommendationExplanationRequest,
    RecommendationExplanationResponse,
    RecommendedExercise,
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
        confidence = 0.5
        strategy = request.strategy
        reason = "Recommended the first available exercise because no mastery profile exists yet."
        if exercise is not None:
            reason = build_ai_recommendation_reason(
                db,
                student_id,
                exercise,
                strategy,
                confidence,
                reason,
            )

        return NextRecommendationResponse(
            exercise=exercise,
            reason=reason,
            strategy=strategy,
            confidence=confidence,
        )

    exercise_query = (
        select(Exercise.id)
        .join(ExerciseKnowledgeComponent, ExerciseKnowledgeComponent.exercise_id == Exercise.id)
        .where(ExerciseKnowledgeComponent.kc_id == weakest.kc_id)
        .order_by(Exercise.id)
    )
    if request.current_exercise_id:
        exercise_query = exercise_query.where(
            Exercise.id != request.current_exercise_id
        )

    exercise_id = db.scalars(exercise_query).first()

    if exercise_id is None and request.current_exercise_id:
        exercise_id = db.scalars(
            select(Exercise.id)
            .where(Exercise.id != request.current_exercise_id)
            .order_by(Exercise.id)
        ).first()

    exercise = None if exercise_id is None else get_exercise_by_id(db, exercise_id, student_id)
    strategy = "lowest_mastery_with_difficulty_match"
    confidence = 0.82
    reason = (
        f"Recommended because {weakest.kc_id} mastery is "
        f"{weakest.mastery:.2f} below the target threshold."
    )
    if exercise is not None:
        reason = build_ai_recommendation_reason(
            db,
            student_id,
            exercise,
            strategy,
            confidence,
            reason,
        )

    return NextRecommendationResponse(
        exercise=exercise,
        reason=reason,
        strategy=strategy,
        confidence=confidence,
    )


def build_recommendation_reason_from_ai_response(
    explanation: RecommendationExplanationResponse,
) -> str:
    return explanation.student_friendly_reason or explanation.reason


def build_ai_recommendation_reason(
    db: Session,
    student_id: str,
    exercise,
    strategy: str,
    confidence: float,
    fallback_reason: str,
) -> str:
    ai_request = RecommendationExplanationRequest(
        student_id=student_id,
        current_exercise=CurrentExercise(id=exercise.id, title=exercise.title),
        recommended_exercise=RecommendedExercise(
            id=exercise.id,
            title=exercise.title,
            kc_tags=[tag.code for tag in exercise.kcTags],
            difficulty=exercise.difficulty,
        ),
        mastery_profile=get_mastery_profile_map(db, student_id),
        strategy=strategy,
        confidence=confidence,
    )

    try:
        explanation = OpenAIRecommendationExplanationService().generate_explanation(ai_request)
    except LLMGenerationError:
        explanation = create_fallback_explanation(ai_request)

    return build_recommendation_reason_from_ai_response(explanation) or fallback_reason


def get_mastery_profile_map(db: Session, student_id: str) -> dict[str, float]:
    rows = db.execute(
        select(StudentMastery.kc_id, StudentMastery.mastery)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.kc_id)
    ).all()

    return {kc_id: round(mastery, 2) for kc_id, mastery in rows}
