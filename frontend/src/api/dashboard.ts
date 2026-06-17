import { apiRequest } from "@/api/client";
import { getMockDashboard, USE_MOCK_API, wait } from "@/api/mock";
import type { ClassDashboardSummary } from "@/types/tutor";

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
