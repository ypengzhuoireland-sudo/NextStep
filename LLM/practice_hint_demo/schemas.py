from __future__ import annotations

import os
from typing import Any

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


def dump_jsonable(value: BaseModel | dict[str, Any] | list[Any]) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    return value
