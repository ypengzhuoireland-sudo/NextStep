from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.student_access import require_student_user
from app.db.session import get_db
from app.schemas.practice import (
    CurrentExerciseResponse,
    HintMessage,
    HintRequest,
    PracticeSessionCreateRequest,
    PracticeSessionCreateResponse,
)
from app.schemas.sessions import UserProfile
from app.services.practice_service import (
    build_current_exercise_response,
    build_hint_message,
    create_practice_session,
)

router = APIRouter()


@router.post("/sessions", response_model=PracticeSessionCreateResponse)
def create_session(
    request: PracticeSessionCreateRequest,
    current_user: UserProfile = Depends(require_student_user),
    db: Session = Depends(get_db),
) -> PracticeSessionCreateResponse:
    return create_practice_session(db, request, current_user)


@router.get("/session/current-exercise", response_model=CurrentExerciseResponse)
def get_current_exercise(
    session_id: str = Query(default="ses_demo"),
    current_user: UserProfile = Depends(require_student_user),
    db: Session = Depends(get_db),
) -> CurrentExerciseResponse:
    return build_current_exercise_response(db, session_id, current_user)


@router.post("/hints", response_model=HintMessage)
def request_hint(
    request: HintRequest,
    current_user: UserProfile = Depends(require_student_user),
    db: Session = Depends(get_db),
) -> HintMessage:
    try:
        return build_hint_message(db, request, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
