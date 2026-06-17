import assert from "node:assert/strict";
import test from "node:test";

import {
  appendExerciseHistory,
  takePreviousExercise
} from "../src/hooks/exerciseHistory.ts";

test("returns exercises in reverse visit order without mutating history", () => {
  const exerciseA = { id: "A" };
  const exerciseB = { id: "B" };
  const original = [exerciseA];
  const history = appendExerciseHistory(original, exerciseB, { id: "C" });

  assert.deepEqual(original, [exerciseA]);
  assert.deepEqual(history, [exerciseA, exerciseB]);

  const first = takePreviousExercise(history);
  assert.equal(first.previous, exerciseB);
  assert.deepEqual(first.remaining, [exerciseA]);

  const second = takePreviousExercise(first.remaining);
  assert.equal(second.previous, exerciseA);
  assert.deepEqual(second.remaining, []);
});

test("does not add history when the recommendation repeats the current exercise", () => {
  const exercise = { id: "A" };

  assert.deepEqual(
    appendExerciseHistory([], exercise, { id: "A" }),
    []
  );
});

test("returns no previous exercise for empty history", () => {
  assert.deepEqual(takePreviousExercise([]), {
    previous: null,
    remaining: []
  });
});
