import { apiRequest } from "@/api/client";
import { getMockSession, USE_MOCK_API, wait } from "@/api/mock";
import type { PracticeSession, SessionCreateRequest, SessionCreateResponse } from "@/types/tutor";

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

  return apiRequest<SessionCreateResponse>("/sessions", {
    method: "POST",
    body: JSON.stringify({
      display_name: request.displayName,
      preferred_group: request.preferredGroup
    })
  });
}

export async function getCurrentPracticeSession(sessionId?: string): Promise<PracticeSession> {
  if (USE_MOCK_API) {
    await wait(420);
    return getMockSession();
  }

  const params = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : "";
  return apiRequest<PracticeSession>(`/session/current-exercise${params}`);
}
