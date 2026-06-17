from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import ClassDashboardSummary, DashboardResponse
from app.schemas.sessions import UserProfile
from app.services.dashboard_service import build_class_dashboard_summary, build_dashboard_response
from app.services.session_service import get_user_from_access_token


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/dashboard/class-summary", response_model=ClassDashboardSummary)
def class_dashboard_summary(
    class_id: str = Query(default="demo-python-101"),
    db: Session = Depends(get_db),
) -> ClassDashboardSummary:
    return build_class_dashboard_summary(db, class_id)


# Handle the student dashboard API request for the currently logged-in user.
@router.get("/dashboard/student", response_model=DashboardResponse)
def dashboard(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    current_user = get_current_dashboard_user(auth_credentials, db)
    return build_dashboard_response(db, current_user)


# Validate the bearer token and return the matching user profile.
def get_current_dashboard_user(
    auth_credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> UserProfile:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    current_user = get_user_from_access_token(db, auth_credentials.credentials)

    if current_user is None:
        raise_unauthorized("Invalid or expired access token")

    return current_user


# Raise a standard 401 response for missing or invalid dashboard credentials.
def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
