from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.diagnostic import (
    DiagnosticQuestionResponse,
    DiagnosticResultResponse,
    DiagnosticSubmissionRequest,
)
from app.services.diagnostic_service import (
    DiagnosticAlreadyCompletedError,
    DiagnosticValidationError,
    get_diagnostic_questions,
    submit_diagnostic,
)
from app.services.student_auth_service import get_user_model_from_token

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/questions", response_model=DiagnosticQuestionResponse)
def list_diagnostic_questions(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> DiagnosticQuestionResponse:
    get_current_user(auth_credentials, db)
    return get_diagnostic_questions()


@router.post("/submit", response_model=DiagnosticResultResponse)
def submit_diagnostic_answers(
    request: DiagnosticSubmissionRequest,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> DiagnosticResultResponse:
    user = get_current_user(auth_credentials, db)
    try:
        return submit_diagnostic(db, user, request.answers)
    except DiagnosticAlreadyCompletedError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except DiagnosticValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials | None,
    db: Session,
):
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")
    user = get_user_model_from_token(db, auth_credentials.credentials)
    if user is None:
        raise_unauthorized("Invalid or expired student token")
    return user


def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
