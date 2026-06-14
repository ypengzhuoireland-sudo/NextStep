from pydantic import BaseModel


class MasteryKnowledgeComponent(BaseModel):
    code: str
    name: str
    description: str
    mastery: float
    trend: float
    state: str


class StudentMasteryProfile(BaseModel):
    student_id: str
    updated_at: str
    items: list[MasteryKnowledgeComponent]
