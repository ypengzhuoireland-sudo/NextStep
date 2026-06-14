from pydantic import BaseModel


class ExerciseListItem(BaseModel):
    id: str
    title: str
    difficulty: str
    primary_kc: str
    estimated_minutes: int


class ExerciseListResponse(BaseModel):
    items: list[ExerciseListItem]
    total: int


class KnowledgeComponentTag(BaseModel):
    code: str
    name: str
    description: str
    mastery: float
    trend: float
    state: str


class ExerciseExample(BaseModel):
    input: str
    output: str
    explanation: str


class ExerciseRecommendation(BaseModel):
    strategy: str
    reason: str
    confidence: float


class ExerciseDetail(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    estimatedMinutes: int
    prompt: str
    goal: str
    constraints: list[str]
    examples: list[ExerciseExample]
    starterCode: str
    kcTags: list[KnowledgeComponentTag]
    recommendation: ExerciseRecommendation
