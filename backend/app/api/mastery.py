from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mastery import StudentMasteryProfile
from app.schemas.sessions import UserProfile
from app.services.mastery_service import get_student_mastery_profile
from app.services.session_service import get_user_from_access_token


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/mastery/me", response_model=StudentMasteryProfile)
def get_my_mastery(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> StudentMasteryProfile:
    current_user = get_current_mastery_user(auth_credentials, db)
    profile = get_student_mastery_profile(db, current_user.student_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return profile


@router.get("/students/{student_id}/mastery", response_model=StudentMasteryProfile)
def get_student_mastery(
    student_id: str,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> StudentMasteryProfile:
    current_user = get_current_mastery_user(auth_credentials, db)

    if current_user.role != "admin" and current_user.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own mastery profile",
        )

    profile = get_student_mastery_profile(db, student_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return profile


def get_current_mastery_user(
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
