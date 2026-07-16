from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.student_access import require_student_user
from app.db.session import get_db
from app.schemas.submissions import SubmissionCreateRequest, SubmissionResponse
from app.schemas.sessions import UserProfile
from app.services.execution_service import ExecutionServiceError
from app.services.submission_service import create_submission


router = APIRouter()


# Authenticate the current student, process the submitted code, and return test feedback.
@router.post("/submissions", response_model=SubmissionResponse)
def submit_code(
    request: SubmissionCreateRequest,
    current_user: UserProfile = Depends(require_student_user),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    try:
        return create_submission(db, current_user.student_id, request)
    except ExecutionServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
