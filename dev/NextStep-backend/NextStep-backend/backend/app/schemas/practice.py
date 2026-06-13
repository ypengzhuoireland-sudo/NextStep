from typing import Any

from pydantic import BaseModel, Field

from app.schemas.exercises import ExerciseDetail
from app.schemas.mastery import MasteryKnowledgeComponent


class PracticeSessionCreateRequest(BaseModel):
    display_name: str | None = None
    preferred_group: str | None = "adaptive"


class PracticeSessionCreateResponse(BaseModel):
    session_id: str
    student_id: str
    experiment_group: str


class LearningPathItem(BaseModel):
    kcCode: str
    kcName: str
    mastery: float
    state: str
    recommendedExerciseId: str | None = None


class DashboardSeriesPoint(BaseModel):
    label: str
    masteryAverage: float


class HintMessage(BaseModel):
    id: str
    role: str
    level: int
    title: str
    text: str
    kcCode: str
    createdAt: str
    avoid_full_solution: bool


class CurrentExerciseResponse(BaseModel):
    sessionId: str
    studentId: str
    experimentGroup: str
    exercise: ExerciseDetail | None
    masteryProfile: list[MasteryKnowledgeComponent]
    learningPath: list[LearningPathItem]
    dashboardSeries: list[DashboardSeriesPoint]
    latestResult: dict[str, Any] | None
    hintMessages: list[HintMessage]


class HintRequest(BaseModel):
    session_id: str | None = None
    student_id: str | None = None
    exercise_id: str
    latest_submission_id: str | None = None
    requested_hint_level: int = Field(default=1, ge=1)
