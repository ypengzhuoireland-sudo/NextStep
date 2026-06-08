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
  const checks60 = code.includes(">= 60") || code.includes(">=60");
  const passed = mode === "run" ? checks60 : hasAppend && checks60;

  return cloneMock(passed ? mockPassedSubmission : mockFailedSubmission);
}

export function getMockRecommendation(opts: {
  currentExerciseId?: string;
  experimentGroup?: ExperimentGroup;
  masteryProfile?: KnowledgeComponent[];
}): RecommendationResponse {
  const profile = opts.masteryProfile?.length ? opts.masteryProfile : mockSession.masteryProfile;
  const group = opts.experimentGroup ?? mockSession.experimentGroup;
  const pool = getMockExercises();
  const currentId = opts.currentExerciseId ?? mockSession.exercise.id;

  if (group === "fixed") {
    const ex = pool.find((item) => item.id !== currentId) ?? pool[0];
    return packRec(ex, {
      strategy: "fixed_ordering_baseline",
      reason: "Fixed baseline selected the next published exercise in the planned sequence.",
      confidence: 0.72
    });
  }

  if (group === "random") {
    const candidates = pool.filter((exercise) => exercise.id !== currentId);
    const maybe = candidates[Math.floor(Date.now() % Math.max(candidates.length, 1))] ?? pool[0];
    return packRec(maybe, {
      strategy: "random_baseline",
      reason: "Random baseline selected this exercise without using mastery state.",
      confidence: 0.58
    });
  }

  // good enough for demo until backend recommendation logs are wired in
  const weakKcs = [...profile].sort((a, b) => a.mastery - b.mastery);

  for (const kc of weakKcs) {
    const matched = pool.find(
      (exercise) =>
        exercise.id !== currentId &&
        exercise.kcTags.some((tag) => tag.code === kc.code)
    );

    if (matched) {
      return packRec(matched, {
        strategy: "lowest_mastery_with_difficulty_match",
        reason: `${kc.name} mastery is ${kc.mastery.toFixed(
          2
        )}, below the 0.75 target. This exercise targets ${kc.code} while staying within the current difficulty band.`,
        confidence: Math.min(0.94, 0.76 + (0.75 - kc.mastery) * 0.35)
      });
    }
  }

  return packRec(pool.find((item) => item.id !== currentId) ?? pool[0], {
    strategy: "spiral_review",
    reason: "All tracked KCs are near target, so the tutor selected a mixed review exercise.",
    confidence: 0.74
  });
}

function packRec(
  exercise: Exercise,
  rec: Omit<RecommendationResponse, "exercise">
): RecommendationResponse {
  const nextExercise = cloneMock(exercise);
  nextExercise.recommendation = {
    strategy: rec.strategy,
    reason: rec.reason,
    confidence: rec.confidence
  };

  return {
    exercise: nextExercise,
    ...rec
  };
}
