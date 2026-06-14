from pydantic import BaseModel, Field


class LearningAdviceResponse(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    next_steps: list[str]
    warning: str = ""
