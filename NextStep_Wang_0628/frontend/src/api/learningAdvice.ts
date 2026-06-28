import { apiRequest } from "@/api/client";
import { getMockSession, USE_MOCK_API, wait } from "@/api/mock";
import type { LearningAdvice } from "@/types/tutor";

interface LearningAdviceApiResponse {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  next_steps: string[];
  warning: string;
}

export async function getLearningAdvice(): Promise<LearningAdvice> {
  if (USE_MOCK_API) {
    await wait(360);
    return buildMockLearningAdvice();
  }

  const response = await apiRequest<LearningAdviceApiResponse>("/learning-advice/student");
  return mapLearningAdvice(response);
}

function mapLearningAdvice(response: LearningAdviceApiResponse): LearningAdvice {
  return {
    summary: response.summary,
    strengths: response.strengths,
    weaknesses: response.weaknesses,
    nextSteps: response.next_steps,
    warning: response.warning
  };
}

function buildMockLearningAdvice(): LearningAdvice {
  const session = getMockSession();
  const ranked = [...session.masteryProfile].sort((a, b) => a.mastery - b.mastery);
  const weak = ranked.slice(0, 2).map((kc) => kc.name);
  const strong = ranked.slice(-2).reverse().map((kc) => kc.name);

  return {
    summary: `${weak[0] ?? "Core Python"} is the clearest next area to practise based on your current mastery profile.`,
    strengths: strong,
    weaknesses: weak,
    nextSteps: [
      `Complete one focused exercise for ${weak[0] ?? "your weakest KC"}.`,
      "Review the examples before submitting so hidden edge cases are less surprising.",
      "Use one level-1 hint before asking for a stronger hint."
    ],
    warning: ""
  };
}
