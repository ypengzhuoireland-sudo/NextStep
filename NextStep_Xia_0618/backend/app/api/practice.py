from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

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
from app.services.session_service import get_user_from_access_token

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/sessions", response_model=PracticeSessionCreateResponse)
def create_session(
    request: PracticeSessionCreateRequest,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> PracticeSessionCreateResponse:
    current_user = get_optional_user(auth_credentials, db)
    return create_practice_session(db, request, current_user)


@router.get("/session/current-exercise", response_model=CurrentExerciseResponse)
def get_current_exercise(
    session_id: str = Query(default="ses_demo"),
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentExerciseResponse:
    current_user = get_optional_user(auth_credentials, db)
    return build_current_exercise_response(db, session_id, current_user)


@router.post("/hints", response_model=HintMessage)
def request_hint(
    request: HintRequest,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> HintMessage:
    current_user = get_optional_user(auth_credentials, db)

    try:
        return build_hint_message(db, request, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def get_optional_user(
    auth_credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> UserProfile | None:
    if auth_credentials is None:
        return None

    current_user = get_user_from_access_token(db, auth_credentials.credentials)

    if current_user is None:
        raise_unauthorized("Invalid or expired access token")

    return current_user


def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
