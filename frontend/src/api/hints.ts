import { apiRequest } from "@/api/client";
import { USE_MOCK_API, wait } from "@/api/mock";
import type { HintMessage } from "@/types/tutor";

interface HintRequest {
  sessionId?: string;
  studentId?: string;
  exerciseId?: string;
  latestSubmissionId?: string;
  requestedHintLevel: 1 | 2 | 3;
}

export async function requestHint(levelOrRequest: 1 | 2 | 3 | HintRequest): Promise<HintMessage> {
  const request = typeof levelOrRequest === "number" ? { requestedHintLevel: levelOrRequest } : levelOrRequest;

  if (USE_MOCK_API) {
    await wait(980);
    return buildMockHint(request.requestedHintLevel);
  }

  return apiRequest<HintMessage>("/hints", {
    method: "POST",
    body: JSON.stringify({
      session_id: request.sessionId,
      student_id: request.studentId,
      exercise_id: request.exerciseId,
      latest_submission_id: request.latestSubmissionId,
      requested_hint_level: request.requestedHintLevel
    })
  });
}

function buildMockHint(level: 1 | 2 | 3): HintMessage {
  const hintByLevel: Record<1 | 2 | 3, Pick<HintMessage, "title" | "text">> = {
    1: {
      title: "Think about the threshold",
      text:
        "The exercise says scores greater than or equal to 60 should pass. Try reading that phrase as a boolean expression."
    },
    2: {
      title: "Place the branch inside the loop",
      text:
        "Inside `for score in scores`, check whether the current score passes. If it does, add that exact score into `result`."
    },
    3: {
      title: "Worked pattern, not the full solution",
      text:
        "For a list filter, the shape is: create an empty result, loop over each item, use `if item meets_rule`, append it, then return result."
    }
  };

  return {
    id: `hint-${level}-${Date.now()}`,
    role: "assistant",
    level,
    kcCode: "lists",
    createdAt: new Intl.DateTimeFormat("en", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    }).format(new Date()),
    ...hintByLevel[level]
  };
}
