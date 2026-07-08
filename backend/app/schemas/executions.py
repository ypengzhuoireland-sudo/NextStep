from typing import Any

from pydantic import BaseModel, Field


# Define the request body accepted by POST /api/executions/run.
class ExecutionRunRequest(BaseModel):
    session_id: str | None = None
    exercise_id: str | None = None
    code: str = Field(min_length=1)
    language: str = "python"
    stdin: str = ""
    expected_output: str | None = None


class ExecutionTestCase(BaseModel):
    id: str
    label: str
    input: str
    expected: str
    actual: str | None = None
    hidden: bool
    passed: bool
    runtimeMs: int


class MasteryDelta(BaseModel):
    kcCode: str
    before: float
    after: float


class ExecutionRunResponse(BaseModel):
    id: str
    status: str
    summary: str
    errorType: str | None = None
    runtimeMs: int
    memoryMb: float
    passedCount: int
    totalCount: int
    stdout: str
    stderr: str
    testCases: list[ExecutionTestCase]
    masteryDelta: list[MasteryDelta]

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    @property
    def status_description(self) -> str:
        if self.status == "passed":
            return "Accepted"
        if self.status == "failed":
            return "Failed tests"
        return self.summary

    @property
    def status_id(self) -> int | None:
        if self.status == "passed":
            return 3
        if self.errorType == "timeout":
            return 5
        return None
