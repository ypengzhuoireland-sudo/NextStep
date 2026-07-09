from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.student_auth import (
    StudentAuthResponse,
    StudentLoginRequest,
    StudentMessageResponse,
    StudentMeResponse,
    StudentRegisterRequest,
)
from app.services.student_auth_service import (
    authenticate_student,
    authenticate_teacher,
    delete_student_account,
    get_student_from_token,
    logout_student,
    register_student,
)

router = APIRouter(prefix="/auth/student", tags=["student-auth"])
teacher_router = APIRouter(prefix="/auth/teacher", tags=["teacher-auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/login", response_model=StudentAuthResponse)
def login_student(
    request: StudentLoginRequest,
    db: Session = Depends(get_db),
) -> StudentAuthResponse:
    response = authenticate_student(db, request)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return response


@teacher_router.post("/login", response_model=StudentAuthResponse)
def login_teacher(
    request: StudentLoginRequest,
    db: Session = Depends(get_db),
) -> StudentAuthResponse:
    response = authenticate_teacher(db, request)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid teacher email or password",
        )

    return response


@router.post(
    "/register",
    response_model=StudentAuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_student_account(
    request: StudentRegisterRequest,
    db: Session = Depends(get_db),
) -> StudentAuthResponse:
    response = register_student(db, request)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    return response


@router.get("/me", response_model=StudentMeResponse)
def get_student_me(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> StudentMeResponse:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    user = get_student_from_token(db, auth_credentials.credentials)

    if user is None:
        raise_unauthorized("Invalid or expired student token")

    return StudentMeResponse(user=user)


@router.post("/logout", response_model=StudentMessageResponse)
def logout_current_student(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> StudentMessageResponse:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    logged_out = logout_student(db, auth_credentials.credentials)

    if not logged_out:
        raise_unauthorized("Invalid or expired student token")

    return StudentMessageResponse(message="Logged out")


@router.delete("/me", response_model=StudentMessageResponse)
def delete_current_student(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> StudentMessageResponse:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    deleted = delete_student_account(db, auth_credentials.credentials)

    if not deleted:
        raise_unauthorized("Invalid or expired student token")

    return StudentMessageResponse(message="Account deleted")


def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
