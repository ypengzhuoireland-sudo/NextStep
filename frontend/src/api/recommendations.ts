import { apiRequest } from "@/api/client";
import { getMockRecommendation, USE_MOCK_API, wait } from "@/api/mock";
import type { ExperimentGroup, KnowledgeComponent, RecommendationResponse } from "@/types/tutor";

interface NextRecommendationRequest {
  sessionId: string;
  studentId: string;
  currentExerciseId?: string;
  strategy?: ExperimentGroup;
  masteryProfile?: KnowledgeComponent[];
}

export async function getNextRecommendation(
  request: NextRecommendationRequest
): Promise<RecommendationResponse> {
  if (USE_MOCK_API) {
    await wait(780);
    return getMockRecommendation({
      currentExerciseId: request.currentExerciseId,
      experimentGroup: request.strategy,
      masteryProfile: request.masteryProfile
    });
  }

  return apiRequest<RecommendationResponse>("/recommendations/next", {
    method: "POST",
    body: JSON.stringify({
      session_id: request.sessionId,
      student_id: request.studentId,
      current_exercise_id: request.currentExerciseId,
      strategy: request.strategy
    })
  });
}
