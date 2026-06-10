from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.schemas.executions import ExecutionRunRequest, ExecutionRunResponse


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
    output_matches = True

    if request.expected_output is not None:
        output_matches = stdout.strip() == request.expected_output.strip()

    return ExecutionRunResponse(
        passed=accepted and output_matches,
        stdout=stdout,
        stderr=stderr,
        compile_output=compile_output,
        message=message,
        status_id=status_id,
        status_description=status_description,
        time=response.get("time"),
        memory=response.get("memory"),
        token=response.get("token"),
    )
