import { apiRequest } from "@/api/client";
import { getMockSession, USE_MOCK_API, wait } from "@/api/mock";
import type { StudentMasteryProfile } from "@/types/tutor";

interface MasteryApiResponse {
  student_id: string;
  updated_at: string;
  items: StudentMasteryProfile["items"];
}

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

  const response = await apiRequest<MasteryApiResponse>(
    `/students/${encodeURIComponent(studentId)}/mastery`
  );
  
  return {
    studentId: response.student_id,
    updatedAt: response.updated_at,
    items: response.items
  };
}
