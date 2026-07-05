from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ExerciseContext(BaseModel):
    id: str
    title: str
    prompt: str
    kc_tags: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    examples: list[dict[str, str]] = Field(default_factory=list)


class FailedTest(BaseModel):
    input: str = ""
    expected: str = ""
    actual: str = ""


class LatestResult(BaseModel):
    passed: bool = False
    stderr: str = ""
    failed_tests: list[FailedTest] = Field(default_factory=list)


class HintRequest(BaseModel):
    exercise: ExerciseContext
    student_code: str = ""
    latest_result: LatestResult | None = None
    mastery_context: dict[str, float] = Field(default_factory=dict)
    requested_hint_level: int = Field(default=1, ge=1, le=3)

    @field_validator("mastery_context")
    @classmethod
    def clamp_mastery_values(cls, value: dict[str, float]) -> dict[str, float]:
        return {key: max(0.0, min(1.0, float(score))) for key, score in value.items()}


class HintResponse(BaseModel):
    level: int = Field(ge=1, le=3)
    title: str
    hint_text: str
    next_step: str
    kc_code: str
    avoid_full_solution: bool


class CurrentExercise(BaseModel):
    id: str
    title: str


class RecommendedExercise(BaseModel):
    id: str
    title: str
    kc_tags: list[str] = Field(default_factory=list)
    difficulty: str = "easy"


class RecommendationExplanationRequest(BaseModel):
    student_id: str
    current_exercise: CurrentExercise
    recommended_exercise: RecommendedExercise
    mastery_profile: dict[str, float] = Field(default_factory=dict)
    strategy: str
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("mastery_profile")
    @classmethod
    def clamp_mastery_values(cls, value: dict[str, float]) -> dict[str, float]:
        return {key: max(0.0, min(1.0, float(score))) for key, score in value.items()}


class RecommendationExplanationResponse(BaseModel):
    reason: str
    student_friendly_reason: str
    focus_kc: str
    expected_benefit: str
    confidence: float = Field(ge=0.0, le=1.0)


class MasteryProfileItem(BaseModel):
    kc_code: str
    kc_name: str
    mastery: float = Field(ge=0.0, le=1.0)
    trend: float


class RecentSubmission(BaseModel):
    exercise_title: str
    status: str
    kc_code: str
    error_type: str = ""
    created_at: str = ""


class ProgressTrend(BaseModel):
    overall_mastery: float = Field(ge=0.0, le=1.0)
    overall_delta: float


class LearningAdviceRequest(BaseModel):
    audience: Literal["student", "teacher"] = "student"
    student_id: str
    mastery_profile: list[MasteryProfileItem] = Field(default_factory=list)
    recent_submissions: list[RecentSubmission] = Field(default_factory=list)
    progress_trend: ProgressTrend


class LearningAdviceResponse(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list, max_length=5)
    weaknesses: list[str] = Field(default_factory=list, max_length=5)
    next_steps: list[str] = Field(min_length=1, max_length=3)
    warning: str = ""


class AssistantIntentRequest(BaseModel):
    message: str
    available_kcs: dict[str, str] = Field(default_factory=dict)


class AssistantIntent(BaseModel):
    kc_code: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    use_weakest_kc: bool = True


class AssistantIntentResult(BaseModel):
    intent: AssistantIntent
    source: Literal["openai", "fallback"]


class OpenAISettings(BaseModel):
    api_key: str = ""
    model: str = "gpt-5.5"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "OpenAISettings":
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        )


def dump_jsonable(value: BaseModel | dict[str, Any] | list[Any] | None) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [dump_jsonable(item) for item in value]
    return value
