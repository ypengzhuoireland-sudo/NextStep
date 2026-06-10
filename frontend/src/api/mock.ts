import {
  mockClassDashboard,
  mockExerciseCatalog,
  mockFailedSubmission,
  mockPassedSubmission,
  mockSession
} from "@/data/mockTutorData";
import type {
  ClassDashboardSummary,
  Exercise,
  ExperimentGroup,
  KnowledgeComponent,
  PracticeSession,
  RecommendationResponse,
  SubmissionResult
} from "@/types/tutor";

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK !== "false";

export const wait = (ms = 650) => new Promise((resolve) => window.setTimeout(resolve, ms));

export function cloneMock<T>(value: T): T {
  return structuredClone(value);
}

export function getMockSession(): PracticeSession {
  return cloneMock(mockSession);
}

export function getMockExercises(): Exercise[] {
  return cloneMock(mockExerciseCatalog);
}

export function getMockDashboard(): ClassDashboardSummary {
  return cloneMock(mockClassDashboard);
}

export function getMockSubmissionResult(code: string, mode: "run" | "submit"): SubmissionResult {
  const hasAppend = code.includes(".append(");
  const hasThreshold = code.includes(">= 60") || code.includes(">=60");
  const passed = mode === "run" ? hasThreshold : hasAppend && hasThreshold;

  return cloneMock(passed ? mockPassedSubmission : mockFailedSubmission);
}

export function getMockRecommendation(params: {
  currentExerciseId?: string;
  experimentGroup?: ExperimentGroup;
  masteryProfile?: KnowledgeComponent[];
}): RecommendationResponse {
  const masteryProfile = params.masteryProfile?.length ? params.masteryProfile : mockSession.masteryProfile;
  const experimentGroup = params.experimentGroup ?? mockSession.experimentGroup;
  const catalog = getMockExercises();
  const currentExerciseId = params.currentExerciseId ?? mockSession.exercise.id;

  if (experimentGroup === "fixed") {
    return buildRecommendation(catalog, currentExerciseId, {
      strategy: "fixed_ordering_baseline",
      reason: "Fixed baseline selected the next published exercise in the planned sequence.",
      confidence: 0.72
    });
  }

  if (experimentGroup === "random") {
    const available = catalog.filter((exercise) => exercise.id !== currentExerciseId);
    const randomExercise = available[Math.floor(Date.now() % Math.max(available.length, 1))] ?? catalog[0];
    return withRecommendation(randomExercise, {
      strategy: "random_baseline",
      reason: "Random baseline selected this exercise without using mastery state.",
      confidence: 0.58
    });
  }

  const weakKcs = [...masteryProfile].sort((a, b) => a.mastery - b.mastery);

  for (const weakKc of weakKcs) {
    const matched = catalog.find(
      (exercise) =>
        exercise.id !== currentExerciseId &&
        exercise.kcTags.some((kc) => kc.code === weakKc.code)
    );

    if (matched) {
      return withRecommendation(matched, {
        strategy: "lowest_mastery_with_difficulty_match",
        reason: `${weakKc.name} mastery is ${weakKc.mastery.toFixed(
          2
        )}, below the 0.75 target. This exercise targets ${weakKc.code} while staying within the current difficulty band.`,
        confidence: Math.min(0.94, 0.76 + (0.75 - weakKc.mastery) * 0.35)
      });
    }
  }

  return buildRecommendation(catalog, currentExerciseId, {
    strategy: "spiral_review",
    reason: "All tracked KCs are near target, so the tutor selected a mixed review exercise.",
    confidence: 0.74
  });
}

function buildRecommendation(
  catalog: Exercise[],
  currentExerciseId: string | undefined,
  recommendation: Omit<RecommendationResponse, "exercise">
): RecommendationResponse {
  const exercise = catalog.find((item) => item.id !== currentExerciseId) ?? catalog[0];
  return withRecommendation(exercise, recommendation);
}

function withRecommendation(
  exercise: Exercise,
  recommendation: Omit<RecommendationResponse, "exercise">
): RecommendationResponse {
  const nextExercise = cloneMock(exercise);
  nextExercise.recommendation = {
    strategy: recommendation.strategy,
    reason: recommendation.reason,
    confidence: recommendation.confidence
  };

  return {
    exercise: nextExercise,
    ...recommendation
  };
}
