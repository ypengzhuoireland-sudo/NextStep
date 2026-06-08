import { apiRequest } from "@/api/client";
import { getMockDashboard, USE_MOCK_API, wait } from "@/api/mock";
import type { ClassDashboardSummary } from "@/types/tutor";

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

  return apiRequest<ClassDashboardSummary>(
    `/dashboard/class-summary?class_id=${encodeURIComponent(classId)}`
  );
}
