from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.submissions import SubmissionCreateRequest, SubmissionResponse
from app.services.session_service import get_user_from_access_token
from app.services.submission_service import create_submission


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


# Authenticate the current student, process the submitted code, and return test feedback.
@router.post("/submissions", response_model=SubmissionResponse)
def submit_code(
    request: SubmissionCreateRequest,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    current_user = get_user_from_access_token(db, auth_credentials.credentials)

    if current_user is None:
        raise_unauthorized("Invalid or expired access token")

    try:
        return create_submission(db, current_user.student_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Raise the standard Bearer authentication response used by the submissions endpoint.
def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
