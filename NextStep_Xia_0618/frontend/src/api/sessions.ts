import { apiRequest } from "@/api/client";
import { getMockSession, USE_MOCK_API, wait } from "@/api/mock";
import type { PracticeSession, SessionCreateRequest, SessionCreateResponse } from "@/types/tutor";

interface CurrentExerciseApiResponse {
  sessionId: string;
  studentId: string;
  experimentGroup: PracticeSession["experimentGroup"];
  exercise: PracticeSession["exercise"] | null;
  masteryProfile: PracticeSession["masteryProfile"];
  learningPath: Array<{
    kcCode: string;
    kcName: string;
    mastery: number;
    state: string;
    recommendedExerciseId?: string;
  }>;
  dashboardSeries: Array<{
    label: string;
    masteryAverage: number;
  }>;
  latestResult: PracticeSession["latestResult"];
  hintMessages: PracticeSession["hintMessages"];
}

export async function createSession(
  request: SessionCreateRequest = {}
): Promise<SessionCreateResponse> {
  if (USE_MOCK_API) {
    await wait(360);
    const session = getMockSession();
    return {
      sessionId: session.sessionId,
      studentId: session.studentId,
      experimentGroup: request.preferredGroup ?? session.experimentGroup
    };
  }

  const response = await apiRequest<{
    session_id: string;
    student_id: string;
    experiment_group: SessionCreateResponse["experimentGroup"];
  }>("/sessions", {
    method: "POST",
    body: JSON.stringify({
      display_name: request.displayName,
      preferred_group: request.preferredGroup
    })
  });

  return {
    sessionId: response.session_id,
    studentId: response.student_id,
    experimentGroup: response.experiment_group
  };
}

export async function getCurrentPracticeSession(
  sessionId?: string
): Promise<PracticeSession> {
  if (USE_MOCK_API) {
    await wait(420);
    return getMockSession();
  }

  const params = sessionId
    ? `?session_id=${encodeURIComponent(sessionId)}`
    : "";

  const response =
    await apiRequest<CurrentExerciseApiResponse>(
      `/session/current-exercise${params}`
    );

  if (!response.exercise) {
    throw new Error("No exercise is available");
  }

  return {
    sessionId: response.sessionId,
    studentId: response.studentId,
    experimentGroup: response.experimentGroup,
    exercise: response.exercise,
    masteryProfile: response.masteryProfile,
    learningPath: response.learningPath.map(
      (item, index) => ({
        id:
          item.recommendedExerciseId ??
          `path_${item.kcCode}`,
        title: item.kcName,
        kcCode: item.kcCode,
        state: index === 0 ? "current" : "queued",
        etaMinutes: 10,
        difficulty: "easy"
      })
    ),
    dashboardSeries: response.dashboardSeries.map(
      (item) => ({
        name: item.label,
        mastery: item.masteryAverage,
        attempts: 0,
        hints: 0
      })
    ),
    latestResult: response.latestResult,
    hintMessages: response.hintMessages
  };
}
