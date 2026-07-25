from pydantic import BaseModel, Field


class DiagnosticOption(BaseModel):
    id: str
    text: str


class DiagnosticQuestion(BaseModel):
    id: str
    kcId: str
    kcName: str
    prompt: str
    code: str | None = None
    options: list[DiagnosticOption]


class DiagnosticQuestionResponse(BaseModel):
    questions: list[DiagnosticQuestion]
    totalQuestions: int
    estimatedMinutes: int


class DiagnosticAnswer(BaseModel):
    questionId: str
    selectedOptionId: str | None = Field(default=None, min_length=1, max_length=10)


class DiagnosticSubmissionRequest(BaseModel):
    answers: list[DiagnosticAnswer]


class DiagnosticKcResult(BaseModel):
    kcId: str
    kcName: str
    correct: int
    total: int
    accuracy: float
    mastery: float
    level: str


class DiagnosticExerciseRecommendation(BaseModel):
    kcId: str
    kcName: str
    exerciseId: str
    exerciseTitle: str
    difficulty: str
    reason: str


class DiagnosticQuestionResult(BaseModel):
    questionId: str
    prompt: str
    selectedOptionId: str | None
    selectedOptionText: str | None
    correctOptionId: str
    correctOptionText: str
    isCorrect: bool
    skipped: bool


class DiagnosticResultResponse(BaseModel):
    totalQuestions: int
    correctAnswers: int
    overallScore: float
    questionResults: list[DiagnosticQuestionResult]
    kcResults: list[DiagnosticKcResult]
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[DiagnosticExerciseRecommendation]
