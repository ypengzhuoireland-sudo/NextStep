from pydantic import BaseModel, Field

from app.schemas.executions import ExecutionRunResponse
from app.schemas.mastery import MasteryKnowledgeComponent


# Validate the exercise, source code, and language sent to POST /api/submissions.
class SubmissionCreateRequest(BaseModel):
    session_id: str | None = None
    student_id: str | None = None
    exercise_id: str
    code: str = Field(min_length=1)
    language: str = "python"


class SubmissionRecord(BaseModel):
    id: str
    status: str
    correct: bool
    attempt_count: int
    created_at: str


class SubmissionResponse(BaseModel):
    submission: SubmissionRecord
    result: ExecutionRunResponse
    masteryProfile: list[MasteryKnowledgeComponent]
