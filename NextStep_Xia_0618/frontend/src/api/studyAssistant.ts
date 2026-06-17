import { apiRequest } from "./client";
import {
  buildAssistantChatPayload,
  mapAssistantChatResponse,
  type AssistantChatApiResponse,
  type AssistantChatResult
} from "@/features/studyAssistant/assistantApiProtocol";

export type { AssistantChatResult };


/** Ask the authenticated backend assistant to recommend a database exercise. */
export async function chatWithStudyAssistant(
  message: string,
  currentExerciseId: string
): Promise<AssistantChatResult> {
  const response = await apiRequest<AssistantChatApiResponse>(
    "/assistant/chat",
    {
      method: "POST",
      body: JSON.stringify(
        buildAssistantChatPayload(message, currentExerciseId)
      )
    }
  );

  return mapAssistantChatResponse(response);
}
