export interface PreviousExerciseResult<TExercise> {
  previous: TExercise | null;
  remaining: TExercise[];
}

export function appendExerciseHistory<TExercise extends { id: string }>(
  history: TExercise[],
  currentExercise: TExercise,
  nextExercise: Pick<TExercise, "id">
): TExercise[] {
  if (currentExercise.id === nextExercise.id) {
    return history;
  }

  return [...history, currentExercise];
}

export function takePreviousExercise<TExercise>(
  history: TExercise[]
): PreviousExerciseResult<TExercise> {
  if (history.length === 0) {
    return {
      previous: null,
      remaining: []
    };
  }

  return {
    previous: history[history.length - 1],
    remaining: history.slice(0, -1)
  };
}
