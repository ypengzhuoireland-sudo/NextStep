from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.student_mastery import StudentMastery
from app.schemas.assistant import (
    AssistantChatIntent,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantExerciseSummary,
)
from app.services.ai.schemas import AssistantIntentResult


ELIGIBLE_EXERCISE_STATUSES = ("published", "ready")


def build_assistant_recommendation(
    db: Session,
    student_id: str,
    request: AssistantChatRequest,
    intent_result: AssistantIntentResult,
) -> AssistantChatResponse:
    """Build the assistant response by ranking real exercises from the database."""
    mastery_by_kc = _get_mastery_by_kc(db, student_id)
    target_kc = intent_result.intent.kc_code

    # If the student asks generally, route the request to their weakest known KC.
    if target_kc is None and intent_result.intent.use_weakest_kc:
        target_kc = _get_weakest_kc(mastery_by_kc)

    # Only published or ready exercises should be shown to a learner.
    exercises = list(
        db.scalars(
            select(Exercise)
            .where(Exercise.status.in_(ELIGIBLE_EXERCISE_STATUSES))
            .order_by(Exercise.id)
        ).all()
    )
    exercises = _exclude_current_when_possible(
        exercises,
        request.currentExerciseId,
    )

    intent = AssistantChatIntent(
        kcCode=intent_result.intent.kc_code,
        difficulty=intent_result.intent.difficulty,
        useWeakestKc=intent_result.intent.use_weakest_kc,
        source=intent_result.source,
    )

    if not exercises:
        return AssistantChatResponse(
            message="I could not find another published exercise.",
            intent=intent,
            recommendedExercise=None,
            exactMatch=False,
        )

    selected = min(
        exercises,
        key=lambda exercise: (
            -_score_exercise(
                exercise,
                target_kc,
                intent_result.intent.difficulty,
                mastery_by_kc,
            ),
            exercise.id,
        ),
    )
    exact_match = (
        (target_kc is None or selected.kc_id == target_kc)
        and (
            intent_result.intent.difficulty is None
            or selected.difficulty == intent_result.intent.difficulty
        )
    )

    return AssistantChatResponse(
        message=_build_message(
            selected,
            target_kc,
            intent_result.intent.difficulty,
            exact_match,
        ),
        intent=intent,
        recommendedExercise=AssistantExerciseSummary(
            id=selected.id,
            title=selected.title,
            difficulty=selected.difficulty,
            primaryKc=selected.kc_id,
            estimatedMinutes=selected.estimated_minutes,
            status="published",
        ),
        exactMatch=exact_match,
    )


def _get_mastery_by_kc(db: Session, student_id: str) -> dict[str, float]:
    """Load the student's latest mastery value for each KC."""
    rows = db.execute(
        select(StudentMastery.kc_id, StudentMastery.mastery)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.kc_id)
    ).all()
    return {kc_id: mastery for kc_id, mastery in rows}


def _get_weakest_kc(mastery_by_kc: dict[str, float]) -> str | None:
    """Choose the lowest mastery KC with a stable tie break by KC code."""
    if not mastery_by_kc:
        return None
    return min(mastery_by_kc, key=lambda code: (mastery_by_kc[code], code))


def _exclude_current_when_possible(
    exercises: list[Exercise],
    current_exercise_id: str | None,
) -> list[Exercise]:
    """Remove the current exercise unless it is the only available option."""
    if not current_exercise_id:
        return exercises
    alternatives = [
        exercise for exercise in exercises if exercise.id != current_exercise_id
    ]
    return alternatives or exercises


def _score_exercise(
    exercise: Exercise,
    target_kc: str | None,
    difficulty: str | None,
    mastery_by_kc: dict[str, float],
) -> float:
    """Score exercises by requested topic, difficulty, then weaker mastery."""
    score = 0.0
    if target_kc and exercise.kc_id == target_kc:
        score += 100.0
    if difficulty and exercise.difficulty == difficulty:
        score += 30.0
    score += (1.0 - mastery_by_kc.get(exercise.kc_id, 0.0)) * 10.0
    return score


def _build_message(
    exercise: Exercise,
    target_kc: str | None,
    difficulty: str | None,
    exact_match: bool,
) -> str:
    """Create a short learner-facing reason for the chosen exercise."""
    if not exact_match:
        return (
            "I could not find an exact match, so I selected the closest "
            "available exercise."
        )
    if target_kc and difficulty:
        return (
            f"This {exercise.difficulty} exercise matches the topic and "
            "difficulty you requested."
        )
    if target_kc:
        return "This exercise matches the topic you requested."
    return "This exercise targets one of your lowest-mastery knowledge areas."
