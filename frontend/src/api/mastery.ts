import { apiRequest } from "@/api/client";
import { getMockSession, USE_MOCK_API, wait } from "@/api/mock";
import type { StudentMasteryProfile } from "@/types/tutor";

export async function getStudentMastery(studentId: string): Promise<StudentMasteryProfile> {
  if (USE_MOCK_API) {
    await wait(360);
    const session = getMockSession();
    return {
      studentId,
      updatedAt: new Date().toISOString(),
      items: session.masteryProfile
    };
  }

  return apiRequest<StudentMasteryProfile>(`/students/${encodeURIComponent(studentId)}/mastery`);
}
