from fastapi import APIRouter, HTTPException, status

from app.schemas.executions import ExecutionRunRequest, ExecutionRunResponse
from app.services.execution_service import ExecutionServiceError, run_code_with_judge0


router = APIRouter()


# Run submitted code through the configured Judge0 runner.
@router.post("/executions/run", response_model=ExecutionRunResponse)
def run_execution(request: ExecutionRunRequest) -> ExecutionRunResponse:
    try:
        return run_code_with_judge0(request)
    except ExecutionServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
