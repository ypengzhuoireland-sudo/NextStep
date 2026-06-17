from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    currentExerciseId: str | None = None

    @field_validator("message")
    @classmethod
    def trim_message(cls, value: str) -> str:
        """Reject messages that contain only whitespace."""
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("message must not be empty")
        return trimmed


class AssistantChatIntent(BaseModel):
    kcCode: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    useWeakestKc: bool
    source: Literal["openai", "fallback"]


class AssistantExerciseSummary(BaseModel):
    id: str
    title: str
    difficulty: Literal["easy", "medium", "hard"]
    primaryKc: str
    estimatedMinutes: int
    status: Literal["published"]


class AssistantChatResponse(BaseModel):
    message: str
    intent: AssistantChatIntent
    recommendedExercise: AssistantExerciseSummary | None
    exactMatch: bool
