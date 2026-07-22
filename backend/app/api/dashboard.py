from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import (
    ClassDashboardSummary,
    ClassStudentDetailResponse,
    ClassStudentDirectoryResponse,
    DashboardResponse,
)
from app.schemas.sessions import UserProfile
from app.services.dashboard_service import (
    build_class_dashboard_summary,
    build_dashboard_response,
    get_class_student_detail,
    list_class_students,
    teacher_has_class_access,
)
from app.services.session_service import get_user_from_access_token


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/dashboard/class-summary", response_model=ClassDashboardSummary)
def class_dashboard_summary(
    class_id: str = Query(default="demo-python-101"),
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ClassDashboardSummary:
    current_user = get_current_dashboard_user(auth_credentials, db, required_role="teacher")
    require_teacher_class_access(db, current_user, class_id)
    return build_class_dashboard_summary(db, class_id)


# Handle the student dashboard API request for the currently logged-in user.
@router.get("/dashboard/student", response_model=DashboardResponse)
def dashboard(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    current_user = get_current_dashboard_user(auth_credentials, db, required_role="student")
    return build_dashboard_response(db, current_user)


@router.get(
    "/dashboard/classes/{class_id}/students",
    response_model=ClassStudentDirectoryResponse,
)
def class_student_directory(
    class_id: str,
    q: str = Query(default="", max_length=100),
    risk: str = Query(default="all", pattern="^(all|at_risk)$"),
    sort: str = Query(default="risk", pattern="^(risk|name|recent)$"),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ClassStudentDirectoryResponse:
    current_user = get_current_dashboard_user(auth_credentials, db, required_role="teacher")
    require_teacher_class_access(db, current_user, class_id)
    return list_class_students(db, class_id, q, risk, sort, limit, offset)


@router.get(
    "/dashboard/classes/{class_id}/students/{student_id}",
    response_model=ClassStudentDetailResponse,
)
def class_student_detail(
    class_id: str,
    student_id: str,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ClassStudentDetailResponse:
    current_user = get_current_dashboard_user(auth_credentials, db, required_role="teacher")
    require_teacher_class_access(db, current_user, class_id)
    detail = get_class_student_detail(db, class_id, student_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found in class")
    return detail


# Validate the bearer token and return the matching user profile.
def get_current_dashboard_user(
    auth_credentials: HTTPAuthorizationCredentials | None,
    db: Session,
    required_role: str | None = None,
) -> UserProfile:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    current_user = get_user_from_access_token(db, auth_credentials.credentials)

    if current_user is None:
        raise_unauthorized("Invalid or expired access token")

    if required_role is not None and current_user.role != required_role:
        raise_forbidden(f"{required_role.title()} role required")

    return current_user


# Raise a standard 401 response for missing or invalid dashboard credentials.
def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# Raise a standard 403 response when a logged-in user has the wrong role.
def raise_forbidden(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def require_teacher_class_access(
    db: Session,
    current_user: UserProfile,
    class_id: str,
) -> None:
    if not teacher_has_class_access(db, current_user.student_id, class_id):
        raise_forbidden("You do not have access to this class")
