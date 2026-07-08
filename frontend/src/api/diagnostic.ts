import { apiRequest } from "@/api/client";

export interface DiagnosticOption {
  id: string;
  text: string;
}

export interface DiagnosticQuestion {
  id: string;
  kcId: string;
  kcName: string;
  prompt: string;
  code?: string | null;
  options: DiagnosticOption[];
}

export interface DiagnosticQuestionResponse {
  questions: DiagnosticQuestion[];
  totalQuestions: number;
  estimatedMinutes: number;
}

export interface DiagnosticKcResult {
  kcId: string;
  kcName: string;
  correct: number;
  total: number;
  accuracy: number;
  mastery: number;
  level: "strength" | "developing" | "weakness";
}

export interface DiagnosticRecommendation {
  kcId: string;
  kcName: string;
  exerciseId: string;
  exerciseTitle: string;
  difficulty: string;
  reason: string;
}

export interface DiagnosticResult {
  totalQuestions: number;
  correctAnswers: number;
  overallScore: number;
  kcResults: DiagnosticKcResult[];
  strengths: string[];
  weaknesses: string[];
  recommendations: DiagnosticRecommendation[];
}

export async function getDiagnosticQuestions(): Promise<DiagnosticQuestionResponse> {
  return apiRequest<DiagnosticQuestionResponse>("/diagnostic/questions");
}

export async function submitDiagnosticAnswers(
  answers: Record<string, string>
): Promise<DiagnosticResult> {
  return apiRequest<DiagnosticResult>("/diagnostic/submit", {
    method: "POST",
    body: JSON.stringify({
      answers: Object.entries(answers).map(([questionId, selectedOptionId]) => ({
        questionId,
        selectedOptionId
      }))
    })
  });
}
