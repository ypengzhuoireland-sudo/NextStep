from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.exercises import ExerciseDetail, ExerciseListResponse
from app.services.exercise_service import get_exercise_by_id, list_exercises


router = APIRouter()


# Return exercise summaries, optionally filtered by KC or difficulty.
@router.get("/exercises", response_model=ExerciseListResponse)
def get_exercises(
    kc: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ExerciseListResponse:
    return list_exercises(db, kc=kc, difficulty=difficulty, status=status)


# Return full details for one exercise so the practice page can render it.
@router.get("/exercises/{exercise_id}", response_model=ExerciseDetail)
def get_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
) -> ExerciseDetail:
    exercise = get_exercise_by_id(db, exercise_id)

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    return exercise
