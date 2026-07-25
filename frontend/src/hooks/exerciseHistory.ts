export interface PreviousExerciseResult<TExercise> {
  previous: TExercise | null;
  remaining: TExercise[];
}

/** Append exercise history. */
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

/** Take previous exercise. */
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
