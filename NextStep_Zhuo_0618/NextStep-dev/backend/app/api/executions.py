from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exercise import Exercise
from app.schemas.executions import ExecutionRunRequest, ExecutionRunResponse
from app.services.execution_service import (
    ExecutionServiceError,
    build_execution_response_from_test_cases,
    execute_code_request,
    run_code_with_judge0,
)
from app.services.test_harness import build_python_test_runner_code, parse_runner_stdout


router = APIRouter()


# Run submitted code through the configured Judge0 runner.
@router.post("/executions/run", response_model=ExecutionRunResponse)
def run_execution(
    request: ExecutionRunRequest,
    db: Session = Depends(get_db),
) -> ExecutionRunResponse:
    try:
        if request.exercise_id is not None:
            exercise = db.get(Exercise, request.exercise_id)

            if exercise is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exercise not found",
                )

            runner_code = build_python_test_runner_code(
                student_code=request.code,
                function_name=exercise.function_name,
                test_cases=exercise.test_cases,
            )
            runner_request = ExecutionRunRequest(code=runner_code, language=request.language)
            response_data = execute_code_request(runner_request)
            test_results = parse_runner_stdout(response_data.get("stdout") or "")

            return build_execution_response_from_test_cases(response_data, test_results)

        return run_code_with_judge0(request)
    except ExecutionServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
