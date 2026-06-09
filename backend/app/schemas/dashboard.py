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


class DashboardTotals(BaseModel):
    students: int
    averageMastery: float
    submissions7d: int
    hintRequests7d: int
    atRiskCount: int


class ClassHeatmapCell(BaseModel):
    studentId: str
    displayName: str
    kcCode: str
    kcName: str
    mastery: float


class RiskStudent(BaseModel):
    studentId: str
    displayName: str
    averageMastery: float
    failedAttempts7d: int
    hintsUsed7d: int
    weakestKc: str
    lastActiveAt: str


class WeakKcSummary(BaseModel):
    kcCode: str
    kcName: str
    averageMastery: float
    affectedStudents: int
    trend: float


class RecentSubmission(BaseModel):
    id: str
    studentId: str
    displayName: str
    exerciseTitle: str
    kcCode: str
    status: str
    passedCount: int
    totalCount: int
    runtimeMs: int
    createdAt: str


class ClassDashboardSummary(BaseModel):
    classId: str
    updatedAt: str
    totals: DashboardTotals
    heatmap: list[ClassHeatmapCell]
    riskStudents: list[RiskStudent]
    weakKcs: list[WeakKcSummary]
    recentSubmissions: list[RecentSubmission]
