import type { Difficulty, ExerciseListItem } from "../../types/tutor.ts";


export interface AssistantChatApiResponse {
  message: string;
  intent: {
    kcCode: string | null;
    difficulty: Difficulty | null;
    useWeakestKc: boolean;
    source: "openai" | "fallback";
  };
  recommendedExercise: {
    id: string;
    title: string;
    difficulty: Difficulty;
    primaryKc: string;
    estimatedMinutes: number;
    status: "published";
  } | null;
  exactMatch: boolean;
}

export interface AssistantChatResult {
  exercise: ExerciseListItem | null;
  reason: string;
  exactMatch: boolean;
  intentSource: "openai" | "fallback";
}


/** Build the request body expected by the backend assistant endpoint. */
export function buildAssistantChatPayload(
  message: string,
  currentExerciseId: string
) {
  return {
    message: message.trim(),
    currentExerciseId
  };
}


/** Convert the backend response into the shape used by the dialog. */
export function mapAssistantChatResponse(
  response: AssistantChatApiResponse
): AssistantChatResult {
  return {
    exercise: response.recommendedExercise,
    reason: response.message,
    exactMatch: response.exactMatch,
    intentSource: response.intent.source
  };
}
