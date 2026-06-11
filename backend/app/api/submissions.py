from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.submissions import SubmissionCreateRequest, SubmissionResponse
from app.services.execution_service import ExecutionServiceError
from app.services.session_service import get_user_from_access_token
from app.services.submission_service import create_submission


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)
DEFAULT_STUDENT_ID = "s1"


# Authenticate the current student, process the submitted code, and return test feedback.
@router.post("/submissions", response_model=SubmissionResponse)
def submit_code(
    request: SubmissionCreateRequest,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    current_user = None

    if auth_credentials is not None:
        current_user = get_user_from_access_token(db, auth_credentials.credentials)

        if current_user is None:
            raise_unauthorized("Invalid or expired access token")

    student_id = (
        current_user.student_id
        if current_user is not None
        else request.student_id or DEFAULT_STUDENT_ID
    )

    try:
        return create_submission(db, student_id, request)
    except ExecutionServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Raise the standard Bearer authentication response used by the submissions endpoint.
def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
