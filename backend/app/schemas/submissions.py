from typing import Any

from pydantic import BaseModel, Field


# Validate the exercise, source code, and language sent to POST /api/submissions.
class SubmissionCreateRequest(BaseModel):
    exercise_id: str
    code: str = Field(min_length=1)
    language: str = "python"


# Represent the expected value, actual value, and outcome of one test case.
class SubmissionTestResult(BaseModel):
    name: str
    passed: bool
    input: Any
    expected_output: Any
    actual_output: Any = None
    error: str = ""


# Define the saved submission, test feedback, mastery update, and recommendation response.
class SubmissionResponse(BaseModel):
    submission_id: int
    exercise_id: str
    passed: bool
    score: float
    stdout: str
    stderr: str
    status_description: str
    test_results: list[SubmissionTestResult]
    updated_mastery: dict[str, float]
    recommended_exercise_id: str | None
