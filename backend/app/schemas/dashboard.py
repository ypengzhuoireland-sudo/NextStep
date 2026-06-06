from pydantic import BaseModel


# Represent one KC mastery item shown on the dashboard.
class KnowledgeComponent(BaseModel):
    id: str
    name: str
    mastery: float


# Represent one exercise summary shown on the dashboard.
class Exercise(BaseModel):
    id: str
    title: str
    kc: str
    difficulty: str
    status: str


# Represent the full dashboard response returned to the logged-in user.
class DashboardResponse(BaseModel):
    student_name: str
    active_goal: str
    backend_status: str
    mastery_average: float
    recommended_exercise_id: str
    knowledge_components: list[KnowledgeComponent]
    exercises: list[Exercise]
