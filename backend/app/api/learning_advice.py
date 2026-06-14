from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.learning_advice import LearningAdviceResponse
from app.schemas.sessions import UserProfile
from app.services.learning_advice_service import build_student_learning_advice
from app.services.session_service import get_user_from_access_token


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/learning-advice/student", response_model=LearningAdviceResponse)
def current_student_learning_advice(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> LearningAdviceResponse:
    current_user = get_current_learning_advice_user(auth_credentials, db)
    return build_student_learning_advice(db, current_user.student_id)


@router.get("/learning-advice/student/{student_id}", response_model=LearningAdviceResponse)
def student_learning_advice(
    student_id: str,
    db: Session = Depends(get_db),
) -> LearningAdviceResponse:
    return build_student_learning_advice(db, student_id)


def get_current_learning_advice_user(
    auth_credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> UserProfile:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

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
