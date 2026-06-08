import { apiRequest } from "@/api/client";
import { getMockSubmissionResult, USE_MOCK_API, wait } from "@/api/mock";
import type { SubmissionResult } from "@/types/tutor";

interface CodeExecutionRequest {
  sessionId?: string;
  studentId?: string;
  exerciseId?: string;
  language?: "python";
  code: string;
}

interface SubmissionApiResponse {
  result: SubmissionResult;
  masteryProfile?: unknown[];
}

export async function runCode(codeOrRequest: string | CodeExecutionRequest): Promise<SubmissionResult> {
  const req = normalizeCodeRequest(codeOrRequest);

  if (USE_MOCK_API) {
    await wait(850);
    return getMockSubmissionResult(req.code, "run");
  }

  return apiRequest<SubmissionResult>("/executions/run", {
    method: "POST",
    body: JSON.stringify({
      session_id: req.sessionId,
      student_id: req.studentId,
      exercise_id: req.exerciseId,
      language: req.language ?? "python",
      code: req.code
    })
  });
}

export async function submitCode(codeOrRequest: string | CodeExecutionRequest): Promise<SubmissionResult> {
  const req = normalizeCodeRequest(codeOrRequest);

  if (USE_MOCK_API) {
    await wait(1180);
    return getMockSubmissionResult(req.code, "submit");
  }

  const res = await apiRequest<SubmissionApiResponse>("/submissions", {
    method: "POST",
    body: JSON.stringify({
      session_id: req.sessionId,
      student_id: req.studentId,
      exercise_id: req.exerciseId,
      language: req.language ?? "python",
      code: req.code
    })
  });

  return res.result;
}

function normalizeCodeRequest(codeOrRequest: string | CodeExecutionRequest): CodeExecutionRequest {
  if (typeof codeOrRequest === "string") {
    return {
      code: codeOrRequest,
      language: "python"
    };
  }

  return {
    language: "python",
    ...codeOrRequest
  };
}
