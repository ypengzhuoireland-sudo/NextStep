import { apiRequest } from "@/api/client";
import { getMockExercises, USE_MOCK_API, wait } from "@/api/mock";
import type { Difficulty, Exercise, ExerciseListResponse } from "@/types/tutor";

interface ExerciseQuery {
  kc?: string;
  difficulty?: Difficulty;
  status?: "published" | "draft";
}

interface ExerciseListApiResponse {
  items: Array<{
    id: string;
    title: string;
    difficulty: Difficulty;
    primary_kc: string;
    estimated_minutes: number;
  }>;
  total: number;
}

export async function getExercises(query: ExerciseQuery = {}): Promise<ExerciseListResponse> {
  if (USE_MOCK_API) {
    await wait(340);
    const items = getMockExercises()
      .filter((exercise) => !query.kc || exercise.kcTags.some((kc) => kc.code === query.kc))
      .filter((exercise) => !query.difficulty || exercise.difficulty === query.difficulty)
      .map((exercise) => ({
        id: exercise.id,
        title: exercise.title,
        difficulty: exercise.difficulty,
        primaryKc: exercise.kcTags[0]?.code ?? "python_basics",
        estimatedMinutes: exercise.estimatedMinutes,
        status: query.status ?? ("published" as const)
      }));

    return {
      items,
      total: items.length
    };
  }

  const params = new URLSearchParams();
  if (query.kc) {
    params.set("kc", query.kc);
  }
  if (query.difficulty) {
    params.set("difficulty", query.difficulty);
  }
  if (query.status) {
    params.set("status", query.status);
  }

  const suffix = params.size
    ? `?${params.toString()}`
    : "";

  const response =
    await apiRequest<ExerciseListApiResponse>(
      `/exercises${suffix}`
    );

  return {
    items: response.items.map((item) => ({
      id: item.id,
      title: item.title,
      difficulty: item.difficulty,
      primaryKc: item.primary_kc,
      estimatedMinutes: item.estimated_minutes,
      status: query.status ?? "published"
    })),
    total: response.total
  };
}

export async function getExerciseById(exerciseId: string): Promise<Exercise> {
  if (USE_MOCK_API) {
    await wait(260);
    const exercise = getMockExercises().find((item) => item.id === exerciseId);
    if (!exercise) {
      throw new Error(`Exercise not found: ${exerciseId}`);
    }
    return exercise;
  }

  return apiRequest<Exercise>(`/exercises/${encodeURIComponent(exerciseId)}`);
}
