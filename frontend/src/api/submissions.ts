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
  const request = normalizeCodeRequest(codeOrRequest);

  if (USE_MOCK_API) {
    await wait(850);
    return getMockSubmissionResult(request.code, "run");
  }

  return apiRequest<SubmissionResult>("/executions/run", {
    method: "POST",
    body: JSON.stringify(toServerPayload(request))
  });
}

export async function submitCode(codeOrRequest: string | CodeExecutionRequest): Promise<SubmissionResult> {
  const request = normalizeCodeRequest(codeOrRequest);

  if (USE_MOCK_API) {
    await wait(1180);
    return getMockSubmissionResult(request.code, "submit");
  }

  const response = await apiRequest<SubmissionApiResponse>("/submissions", {
    method: "POST",
    body: JSON.stringify(toServerPayload(request))
  });

  return response.result;
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

function toServerPayload(request: CodeExecutionRequest) {
  return {
    session_id: request.sessionId,
    student_id: request.studentId,
    exercise_id: request.exerciseId,
    language: request.language ?? "python",
    code: request.code
  };
}
