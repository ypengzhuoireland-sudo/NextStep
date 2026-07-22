import { apiRequest } from "@/api/client";
import { getMockDashboard, USE_MOCK_API, wait } from "@/api/mock";
import type {
  ClassDashboardSummary,
  ClassStudentDetail,
  ClassStudentDirectory,
  MasteryState,
  StudentDashboardSummary
} from "@/types/tutor";

interface ClassDashboardApiResponse {
  class_id: string;
  updated_at: string;
  totals: {
    students: number;
    average_mastery: number;
    submissions_7d: number;
    hint_requests_7d: number;
    at_risk_count: number;
  };
  heatmap: Array<{
    student_id: string;
    display_name: string;
    kc_code: string;
    kc_name: string;
    kc_short_name?: string | null;
    mastery: number;
  }>;
  risk_students: Array<{
    student_id: string;
    display_name: string;
    average_mastery: number;
    failed_attempts_7d: number;
    hints_used_7d: number;
    weakest_kc: string;
    last_active_at: string;
  }>;
  weak_kcs: Array<{
    kc_code: string;
    kc_name: string;
    average_mastery: number;
    affected_students: number;
    trend: number;
  }>;
  recent_submissions: Array<{
    id: string;
    student_id: string;
    display_name: string;
    exercise_title: string;
    kc_code: string;
    status: "idle" | "running" | "passed" | "failed" | "error";
    passed_count: number;
    total_count: number;
    runtime_ms: number;
    created_at: string;
  }>;
}

interface StudentDashboardApiResponse {
  studentId: string;
  studentName: string;
  activeGoal: string;
  backendStatus: string;
  masteryAverage: number;
  recommendedExerciseId: string;
  recommendedExercise: StudentDashboardSummary["recommendedExercise"];
  masteryProfile: Array<{
    id: string;
    code: string;
    name: string;
    shortName?: string | null;
    description: string;
    mastery: number;
    trend: number;
    state: StudentDashboardSummary["masteryProfile"][number]["state"];
  }>;
  learningPath: Array<{
    id: string;
    code: string;
    name: string;
    shortName?: string | null;
    description: string;
    mastery: number;
    trend: number;
    state: StudentDashboardSummary["learningPath"][number]["state"];
  }>;
}

interface ClassStudentDirectoryApiResponse {
  items: Array<{
    student_id: string;
    display_name: string;
    average_mastery: number;
    risk_level: "at_risk" | "on_track";
    weakest_kc: string;
    last_active_at: string;
  }>;
  total: number;
  next_offset: number | null;
}

interface ClassStudentDetailApiResponse {
  student: ClassStudentDirectoryApiResponse["items"][number];
  mastery_profile: ClassStudentDetail["masteryProfile"];
  weak_kcs: ClassStudentDetail["weakKcs"];
  activity: {
    submissions_7d: number;
    failed_attempts_7d: number;
    hints_used_7d: number;
    recent_submissions: Array<{
      id: string;
      student_id: string;
      display_name: string;
      exercise_title: string;
      kc_code: string;
      status: ClassStudentDetail["activity"]["recentSubmissions"][number]["status"];
      passed_count: number;
      total_count: number;
      runtime_ms: number;
      created_at: string;
    }>;
  };
}

export async function getStudentDashboardSummary(): Promise<StudentDashboardSummary> {
  if (USE_MOCK_API) {
    await wait(420);
    const dashboard = getMockDashboard();
    const studentId = dashboard.heatmap[0]?.studentId ?? "stu_mock";
    const profile = dashboard.heatmap
      .filter((item) => item.studentId === studentId)
      .map((item) => ({
        code: item.kcCode,
        name: item.kcName,
        shortName: item.kcShortName,
        description: item.kcName,
        mastery: item.mastery,
        trend: 0,
        state: (item.mastery >= 0.75
          ? "mastered"
          : item.mastery >= 0.5
            ? "almost_there"
            : "needs_practice") as MasteryState
      }));

    return {
      studentId,
      studentName: dashboard.heatmap[0]?.displayName ?? "Mock Student",
      activeGoal: "Practice weak Python concepts",
      backendStatus: "mock",
      masteryAverage: profile.length
        ? profile.reduce((sum, item) => sum + item.mastery, 0) / profile.length
        : 0,
      recommendedExerciseId: "",
      recommendedExercise: null,
      masteryProfile: profile,
      learningPath: [...profile].sort((a, b) => a.mastery - b.mastery).slice(0, 5)
    };
  }

  return apiRequest<StudentDashboardApiResponse>("/dashboard/student");
}

export async function getClassDashboardSummary(
  classId = "demo-python-101"
): Promise<ClassDashboardSummary> {
  if (USE_MOCK_API) {
    await wait(520);
    const dashboard = getMockDashboard();
    return {
      ...dashboard,
      classId
    };
  }

  const response =
    await apiRequest<ClassDashboardApiResponse>(
      `/dashboard/class-summary?class_id=${encodeURIComponent(classId)}`
    );

  return {
    classId: response.class_id,
    updatedAt: response.updated_at,
    totals: {
      students: response.totals.students,
      averageMastery: response.totals.average_mastery,
      submissions7d: response.totals.submissions_7d,
      hintRequests7d: response.totals.hint_requests_7d,
      atRiskCount: response.totals.at_risk_count
    },
    heatmap: response.heatmap.map((item) => ({
      studentId: item.student_id,
      displayName: item.display_name,
      kcCode: item.kc_code,
      kcName: item.kc_name,
      kcShortName: item.kc_short_name,
      mastery: item.mastery
    })),
    riskStudents: response.risk_students.map((item) => ({
      studentId: item.student_id,
      displayName: item.display_name,
      averageMastery: item.average_mastery,
      failedAttempts7d: item.failed_attempts_7d,
      hintsUsed7d: item.hints_used_7d,
      weakestKc: item.weakest_kc,
      lastActiveAt: item.last_active_at
    })),
    weakKcs: response.weak_kcs.map((item) => ({
      kcCode: item.kc_code,
      kcName: item.kc_name,
      averageMastery: item.average_mastery,
      affectedStudents: item.affected_students,
      trend: item.trend
    })),
    recentSubmissions: response.recent_submissions.map(
      (item) => ({
        id: item.id,
        studentId: item.student_id,
        displayName: item.display_name,
        exerciseTitle: item.exercise_title,
        kcCode: item.kc_code,
        status: item.status,
        passedCount: item.passed_count,
        totalCount: item.total_count,
        runtimeMs: item.runtime_ms,
        createdAt: item.created_at
      })
    )
  };
}

export interface StudentDirectoryQuery {
  query?: string;
  risk?: "all" | "at_risk";
  sort?: "risk" | "name" | "recent";
  limit?: number;
  offset?: number;
}

export async function getClassStudentDirectory(
  classId: string,
  query: StudentDirectoryQuery = {}
): Promise<ClassStudentDirectory> {
  if (USE_MOCK_API) {
    await wait(220);
    const dashboard = getMockDashboard();
    const studentRows = Array.from(
      new Map(
        dashboard.heatmap.map((cell) => [cell.studentId, cell])
      ).values()
    ).map((cell) => {
      const profile = dashboard.heatmap.filter((item) => item.studentId === cell.studentId);
      const averageMastery = profile.length
        ? profile.reduce((total, item) => total + item.mastery, 0) / profile.length
        : 0;
      const weakest = [...profile].sort((left, right) => left.mastery - right.mastery)[0];
      const risk = dashboard.riskStudents.find((item) => item.studentId === cell.studentId);
      return {
        studentId: cell.studentId,
        displayName: cell.displayName,
        averageMastery,
        riskLevel: averageMastery < 0.6 ? ("at_risk" as const) : ("on_track" as const),
        weakestKc: weakest?.kcName ?? "No KC data",
        lastActiveAt: risk?.lastActiveAt ?? "No recent activity"
      };
    });
    const term = query.query?.trim().toLowerCase() ?? "";
    const filtered = studentRows
      .filter((student) => !term || `${student.displayName} ${student.studentId}`.toLowerCase().includes(term))
      .filter((student) => query.risk !== "at_risk" || student.riskLevel === "at_risk")
      .sort((left, right) => {
        if (query.sort === "name") {
          return left.displayName.localeCompare(right.displayName);
        }
        return left.averageMastery - right.averageMastery;
      });
    const offset = query.offset ?? 0;
    const limit = query.limit ?? 20;
    return {
      items: filtered.slice(offset, offset + limit),
      total: filtered.length,
      nextOffset: offset + limit < filtered.length ? offset + limit : null
    };
  }

  const params = new URLSearchParams();
  if (query.query) params.set("q", query.query);
  if (query.risk) params.set("risk", query.risk);
  if (query.sort) params.set("sort", query.sort);
  if (query.limit) params.set("limit", String(query.limit));
  if (query.offset) params.set("offset", String(query.offset));
  const response = await apiRequest<ClassStudentDirectoryApiResponse>(
    `/dashboard/classes/${encodeURIComponent(classId)}/students?${params.toString()}`
  );
  return {
    items: response.items.map(mapDirectoryItem),
    total: response.total,
    nextOffset: response.next_offset
  };
}

export async function getClassStudentDetail(
  classId: string,
  studentId: string
): Promise<ClassStudentDetail> {
  if (USE_MOCK_API) {
    const directory = await getClassStudentDirectory(classId, { query: studentId });
    const student = directory.items.find((item) => item.studentId === studentId);
    if (!student) throw new Error("Student not found in class");
    const dashboard = getMockDashboard();
    const masteryProfile = dashboard.heatmap
      .filter((cell) => cell.studentId === studentId)
      .map((cell) => ({
        code: cell.kcCode,
        name: cell.kcName,
        shortName: cell.kcShortName,
        description: cell.kcName,
        mastery: cell.mastery,
        trend: 0,
        state: (cell.mastery >= 0.75 ? "mastered" : cell.mastery >= 0.6 ? "almost_there" : "needs_practice") as MasteryState
      }));
    const recentSubmissions = dashboard.recentSubmissions.filter((item) => item.studentId === studentId);
    return {
      student,
      masteryProfile,
      weakKcs: [...masteryProfile].sort((left, right) => left.mastery - right.mastery).slice(0, 3),
      activity: {
        submissions7d: recentSubmissions.length,
        failedAttempts7d: recentSubmissions.filter((item) => item.status !== "passed").length,
        hintsUsed7d: 0,
        recentSubmissions
      }
    };
  }

  const response = await apiRequest<ClassStudentDetailApiResponse>(
    `/dashboard/classes/${encodeURIComponent(classId)}/students/${encodeURIComponent(studentId)}`
  );
  return {
    student: mapDirectoryItem(response.student),
    masteryProfile: response.mastery_profile,
    weakKcs: response.weak_kcs,
    activity: {
      submissions7d: response.activity.submissions_7d,
      failedAttempts7d: response.activity.failed_attempts_7d,
      hintsUsed7d: response.activity.hints_used_7d,
      recentSubmissions: response.activity.recent_submissions.map((item) => ({
        id: item.id,
        studentId: item.student_id,
        displayName: item.display_name,
        exerciseTitle: item.exercise_title,
        kcCode: item.kc_code,
        status: item.status,
        passedCount: item.passed_count,
        totalCount: item.total_count,
        runtimeMs: item.runtime_ms,
        createdAt: item.created_at
      }))
    }
  };
}

function mapDirectoryItem(item: ClassStudentDirectoryApiResponse["items"][number]) {
  return {
    studentId: item.student_id,
    displayName: item.display_name,
    averageMastery: item.average_mastery,
    riskLevel: item.risk_level,
    weakestKc: item.weakest_kc,
    lastActiveAt: item.last_active_at
  };
}
