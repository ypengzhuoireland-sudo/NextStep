from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise as ExerciseModel
from app.schemas.exercises import ExerciseDetail, ExerciseSummary


# Query PostgreSQL and return lightweight exercise items for lists and queues.
def list_exercises(
    db: Session,
    kc: str | None = None,
    difficulty: str | None = None,
) -> list[ExerciseSummary]:
    statement = select(ExerciseModel).order_by(ExerciseModel.id)

    if kc is not None:
        statement = statement.where(ExerciseModel.kc_id == kc)

    if difficulty is not None:
        statement = statement.where(ExerciseModel.difficulty == difficulty)

    exercises = db.scalars(statement).all()

    return [to_exercise_summary(exercise) for exercise in exercises]


# Query PostgreSQL for one full exercise record by id for the practice page.
def get_exercise_by_id(db: Session, exercise_id: str) -> ExerciseDetail | None:
    exercise = db.get(ExerciseModel, exercise_id)

    if exercise is None:
        return None

    return ExerciseDetail(
        id=exercise.id,
        title=exercise.title,
        kc=exercise.kc_id,
        difficulty=exercise.difficulty,
        status=exercise.status,
        description=exercise.description,
        starter_code=exercise.starter_code,
        test_cases=exercise.test_cases,
    )


# Convert a database exercise row into the public list schema.
def to_exercise_summary(exercise: ExerciseModel) -> ExerciseSummary:
    return ExerciseSummary(
        id=exercise.id,
        title=exercise.title,
        kc=exercise.kc_id,
        difficulty=exercise.difficulty,
        status=exercise.status,
    )
