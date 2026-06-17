export type Difficulty = "easy" | "medium" | "hard";

export type MasteryState = "needs_practice" | "almost_there" | "mastered";

export type ExperimentGroup = "adaptive" | "fixed" | "random";

export interface KnowledgeComponent {
  code: string;
  name: string;
  shortName?: string | null;
  description: string;
  mastery: number;
  trend: number;
  state: MasteryState;
}

export interface ExerciseExample {
  input: string;
  output: string;
  explanation: string;
}

export interface Exercise {
  id: string;
  title: string;
  slug: string;
  difficulty: Difficulty;
  estimatedMinutes: number;
  prompt: string;
  goal: string;
  constraints: string[];
  examples: ExerciseExample[];
  starterCode: string;
  kcTags: KnowledgeComponent[];
  recommendation: {
    strategy: string;
    reason: string;
    confidence: number;
  };
}

export type ExecutionStatus = "idle" | "running" | "passed" | "failed" | "error";

export interface TestCaseResult {
  id: string;
  label: string;
  input: string;
  expected: string;
  actual: string;
  hidden: boolean;
  passed: boolean;
  runtimeMs: number;
}

export interface SubmissionResult {
  id: string;
  status: ExecutionStatus;
  summary: string;
  errorType?: "syntax_error" | "runtime_error" | "failed_tests" | "timeout";
  runtimeMs: number;
  memoryMb: number;
  passedCount: number;
  totalCount: number;
  stdout: string;
  stderr: string;
  testCases: TestCaseResult[];
  masteryDelta: Array<{
    kcCode: string;
    before: number;
    after: number;
  }>;
}

export interface HintMessage {
  id: string;
  role: "assistant" | "student";
  level: 1 | 2 | 3;
  title: string;
  text: string;
  kcCode: string;
  createdAt: string;
}

export interface LearningAdvice {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  nextSteps: string[];
  warning: string;
}

export interface LearningPathItem {
  id: string;
  title: string;
  kcCode: string;
  state: "current" | "queued" | "locked" | "done";
  etaMinutes: number;
  difficulty: Difficulty;
}

export interface DashboardPoint {
  name: string;
  mastery: number;
  attempts: number;
  hints: number;
}

export interface PracticeSession {
  sessionId: string;
  studentId: string;
  experimentGroup: ExperimentGroup;
  exercise: Exercise;
  masteryProfile: KnowledgeComponent[];
  learningPath: LearningPathItem[];
  dashboardSeries: DashboardPoint[];
  latestResult: SubmissionResult | null;
  hintMessages: HintMessage[];
}

export interface SessionCreateRequest {
  displayName?: string;
  preferredGroup?: ExperimentGroup;
}

export interface SessionCreateResponse {
  sessionId: string;
  studentId: string;
  experimentGroup: ExperimentGroup;
}

export interface ExerciseListItem {
  id: string;
  title: string;
  difficulty: Difficulty;
  primaryKc: string;
  estimatedMinutes: number;
  status: "published" | "draft";
}

export interface ExerciseListResponse {
  items: ExerciseListItem[];
  total: number;
}

export interface RecommendationResponse {
  exercise: Exercise;
  reason: string;
  strategy: string;
  confidence: number;
}

export interface StudentMasteryProfile {
  studentId: string;
  updatedAt: string;
  items: KnowledgeComponent[];
}

export interface ClassHeatmapCell {
  studentId: string;
  displayName: string;
  kcCode: string;
  kcName: string;
  kcShortName?: string | null;
  mastery: number;
}

export interface RiskStudent {
  studentId: string;
  displayName: string;
  averageMastery: number;
  failedAttempts7d: number;
  hintsUsed7d: number;
  weakestKc: string;
  lastActiveAt: string;
}

export interface WeakKcSummary {
  kcCode: string;
  kcName: string;
  averageMastery: number;
  affectedStudents: number;
  trend: number;
}

export interface RecentSubmission {
  id: string;
  studentId: string;
  displayName: string;
  exerciseTitle: string;
  kcCode: string;
  status: ExecutionStatus;
  passedCount: number;
  totalCount: number;
  runtimeMs: number;
  createdAt: string;
}

export interface ClassDashboardSummary {
  classId: string;
  updatedAt: string;
  totals: {
    students: number;
    averageMastery: number;
    submissions7d: number;
    hintRequests7d: number;
    atRiskCount: number;
  };
  heatmap: ClassHeatmapCell[];
  riskStudents: RiskStudent[];
  weakKcs: WeakKcSummary[];
  recentSubmissions: RecentSubmission[];
}
