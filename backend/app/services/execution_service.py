from __future__ import annotations

import json
import secrets
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.schemas.executions import ExecutionRunRequest, ExecutionRunResponse, ExecutionTestCase
from app.services.test_harness import format_case_value


# Represent execution failures that should be returned as API errors.
class ExecutionServiceError(Exception):
    pass


# Build the Judge0 request body from the frontend execution request.
def build_judge0_payload(
    request: ExecutionRunRequest,
    python_language_id: int | None = None,
) -> dict[str, Any]:
    if request.language != "python":
        raise ExecutionServiceError("Only python is supported in the MVP runner")

    return {
        "language_id": python_language_id or settings.judge0_python_language_id,
        "source_code": request.code,
        "stdin": request.stdin,
    }


# Execute submitted code through Judge0 and return a normalized backend response.
def run_code_with_judge0(request: ExecutionRunRequest) -> ExecutionRunResponse:
    payload = build_judge0_payload(request)
    response_data = submit_to_judge0(payload)

    return normalize_judge0_response(response_data, request)


# Send one synchronous execution request to Judge0.
def submit_to_judge0(payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.judge0_api_key:
        raise ExecutionServiceError("JUDGE0_API_KEY is not configured")

    url = f"{settings.judge0_base_url.rstrip('/')}/submissions?base64_encoded=false&wait=true"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "curl/8.7.1",
        "X-RapidAPI-Host": settings.judge0_api_host,
        "X-RapidAPI-Key": settings.judge0_api_key,
    }
    http_request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(http_request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise ExecutionServiceError(f"Judge0 HTTP error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise ExecutionServiceError(f"Judge0 connection error: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ExecutionServiceError("Judge0 request timed out") from exc


# Convert Judge0's response shape into the API response used by the frontend.
def normalize_judge0_response(
    response: dict[str, Any],
    request: ExecutionRunRequest,
) -> ExecutionRunResponse:
    status = response.get("status") or {}
    status_id = status.get("id")
    stdout = response.get("stdout") or ""
    stderr = response.get("stderr") or ""
    compile_output = response.get("compile_output") or ""
    message = response.get("message") or ""
    status_description = status.get("description") or "Unknown"
    accepted = status_id == 3
    runtime_ms = to_runtime_ms(response.get("time"))
    memory_mb = to_memory_mb(response.get("memory"))
    test_cases: list[ExecutionTestCase] = []

    if request.expected_output is not None:
        actual = stdout.strip()
        expected = request.expected_output.strip()
        test_cases = [
            ExecutionTestCase(
                id="case_1",
                label="Expected stdout",
                input=request.stdin,
                expected=expected,
                actual=actual,
                hidden=False,
                passed=accepted and actual == expected,
                runtimeMs=runtime_ms,
            )
        ]

    total_count = len(test_cases)
    passed_count = sum(1 for test_case in test_cases if test_case.passed)

    if not accepted:
        result_status = "error"
        error_type = map_judge0_error_type(status_id, status_description)
    elif total_count > 0 and passed_count != total_count:
        result_status = "failed"
        error_type = "failed_tests"
    else:
        result_status = "passed"
        error_type = None

    summary = build_summary(result_status, passed_count, total_count, status_description)

    return ExecutionRunResponse(
        id=f"run_{secrets.token_urlsafe(8)}",
        status=result_status,
        summary=summary,
        errorType=error_type,
        runtimeMs=runtime_ms,
        memoryMb=memory_mb,
        passedCount=passed_count,
        totalCount=total_count,
        stdout=stdout,
        stderr=stderr or compile_output or message,
        testCases=test_cases,
        masteryDelta=[],
    )


def build_execution_response_from_test_cases(
    response: dict[str, Any],
    test_results: list[dict[str, Any]],
) -> ExecutionRunResponse:
    status = response.get("status") or {}
    status_id = status.get("id")
    stdout = response.get("stdout") or ""
    stderr = response.get("stderr") or ""
    compile_output = response.get("compile_output") or ""
    message = response.get("message") or ""
    status_description = status.get("description") or "Unknown"
    runtime_ms = to_runtime_ms(response.get("time"))
    memory_mb = to_memory_mb(response.get("memory"))
    accepted = status_id == 3
    test_cases = [
        ExecutionTestCase(
            id=str(item.get("id") or f"case_{index}"),
            label=str(item.get("label") or f"case {index}"),
            input=format_case_value(item.get("input")),
            expected=format_case_value(item.get("expected")),
            actual=format_case_value(item.get("actual")),
            hidden=bool(item.get("hidden")),
            passed=bool(item.get("passed")),
            runtimeMs=int(item.get("runtimeMs") or 0),
        )
        for index, item in enumerate(test_results, start=1)
    ]
    total_count = len(test_cases)
    passed_count = sum(1 for test_case in test_cases if test_case.passed)

    if not accepted:
        result_status = "error"
        error_type = map_judge0_error_type(status_id, status_description)
    elif passed_count == total_count and total_count > 0:
        result_status = "passed"
        error_type = None
    else:
        result_status = "failed"
        error_type = "failed_tests"

    return ExecutionRunResponse(
        id=f"run_{secrets.token_urlsafe(8)}",
        status=result_status,
        summary=build_summary(result_status, passed_count, total_count, status_description),
        errorType=error_type,
        runtimeMs=runtime_ms,
        memoryMb=memory_mb,
        passedCount=passed_count,
        totalCount=total_count,
        stdout=stdout,
        stderr=stderr or compile_output or message,
        testCases=test_cases,
        masteryDelta=[],
    )


def build_summary(
    result_status: str,
    passed_count: int,
    total_count: int,
    status_description: str,
) -> str:
    if result_status == "passed":
        return "All tests passed." if total_count else status_description
    if result_status == "failed":
        return f"{passed_count} of {total_count} tests passed."
    return status_description


def map_judge0_error_type(status_id: int | None, status_description: str) -> str:
    text = status_description.lower()

    if status_id == 5 or "time" in text:
        return "timeout"
    if "compilation" in text or "syntax" in text:
        return "syntax_error"
    if "runtime" in text:
        return "runtime_error"

    return "runtime_error"


def to_runtime_ms(value: Any) -> int:
    try:
        return int(float(value or 0) * 1000)
    except (TypeError, ValueError):
        return 0


def to_memory_mb(value: Any) -> float:
    try:
        return round(float(value or 0) / 1024, 1)
    except (TypeError, ValueError):
        return 0.0
