from pydantic import BaseModel


class MasteryKnowledgeComponent(BaseModel):
    code: str
    name: str
    description: str
    mastery: float
    trend: float
    state: str


class StudentMasteryProfile(BaseModel):
    studentId: str
    updatedAt: str
    items: list[MasteryKnowledgeComponent]
