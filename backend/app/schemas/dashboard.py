from pydantic import BaseModel


# Represent one KC mastery item shown on the dashboard.
class KnowledgeComponent(BaseModel):
    id: str
    code: str
    name: str
    shortName: str | None = None
    description: str
    mastery: float
    trend: float
    state: str


# Represent one exercise summary shown on the dashboard.
class Exercise(BaseModel):
    id: str
    title: str
    kc: str
    primaryKc: str
    difficulty: str
    estimatedMinutes: int
    status: str


# Represent the full dashboard response returned to the logged-in user.
class DashboardResponse(BaseModel):
    studentId: str
    studentName: str
    activeGoal: str
    backendStatus: str
    masteryAverage: float
    recommendedExerciseId: str
    recommendedExercise: Exercise | None
    masteryProfile: list[KnowledgeComponent]
    learningPath: list[KnowledgeComponent]


class DashboardTotals(BaseModel):
    students: int
    average_mastery: float
    submissions_7d: int
    hint_requests_7d: int
    at_risk_count: int


class ClassHeatmapCell(BaseModel):
    student_id: str
    display_name: str
    kc_code: str
    kc_name: str
    kc_short_name: str | None = None
    mastery: float


class RiskStudent(BaseModel):
    student_id: str
    display_name: str
    average_mastery: float
    failed_attempts_7d: int
    hints_used_7d: int
    weakest_kc: str
    last_active_at: str


class WeakKcSummary(BaseModel):
    kc_code: str
    kc_name: str
    average_mastery: float
    affected_students: int
    trend: float


class RecentSubmission(BaseModel):
    id: str
    student_id: str
    display_name: str
    exercise_title: str
    kc_code: str
    status: str
    passed_count: int
    total_count: int
    runtime_ms: int
    created_at: str


class ClassDashboardSummary(BaseModel):
    class_id: str
    updated_at: str
    totals: DashboardTotals
    heatmap: list[ClassHeatmapCell]
    risk_students: list[RiskStudent]
    weak_kcs: list[WeakKcSummary]
    recent_submissions: list[RecentSubmission]


class ClassStudentDirectoryItem(BaseModel):
    student_id: str
    display_name: str
    average_mastery: float
    risk_level: str
    weakest_kc: str
    last_active_at: str


class ClassStudentDirectoryResponse(BaseModel):
    items: list[ClassStudentDirectoryItem]
    total: int
    next_offset: int | None = None


class ClassStudentDetailHeader(BaseModel):
    student_id: str
    display_name: str
    average_mastery: float
    risk_level: str
    last_active_at: str


class ClassStudentActivity(BaseModel):
    submissions_7d: int
    failed_attempts_7d: int
    hints_used_7d: int
    recent_submissions: list[RecentSubmission]


class ClassStudentDetailResponse(BaseModel):
    student: ClassStudentDetailHeader
    mastery_profile: list[KnowledgeComponent]
    weak_kcs: list[KnowledgeComponent]
    activity: ClassStudentActivity
