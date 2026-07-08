import assert from "node:assert/strict";
import test from "node:test";

import {
  parseAssistantIntent,
  recommendExercise
} from "../src/features/studyAssistant/assistantRecommendation.ts";

const exercises = [
  {
    id: "EX001",
    title: "Variables",
    difficulty: "easy" as const,
    primaryKc: "KC001",
    estimatedMinutes: 5,
    status: "published" as const
  },
  {
    id: "EX010",
    title: "Easy Loops",
    difficulty: "easy" as const,
    primaryKc: "KC003",
    estimatedMinutes: 8,
    status: "published" as const
  },
  {
    id: "EX011",
    title: "Hard Loops",
    difficulty: "hard" as const,
    primaryKc: "KC003",
    estimatedMinutes: 15,
    status: "published" as const
  }
];

const mastery = [
  { code: "KC001", mastery: 0.6 },
  { code: "KC003", mastery: 0.2 }
];

test("parses KC and difficulty aliases", () => {
  assert.deepEqual(parseAssistantIntent("I want an easy loop exercise"), {
    kcCode: "KC003",
    difficulty: "easy",
    useWeakestKc: false
  });
  assert.equal(
    parseAssistantIntent("Give me a beginner list problem").kcCode,
    "KC006"
  );
});

test("uses weakest KC for general practice requests", () => {
  assert.equal(
    parseAssistantIntent("What should I practise?").useWeakestKc,
    true
  );
});

test("selects an exact match and excludes the current exercise", () => {
  const result = recommendExercise({
    message: "Give me a hard loop exercise",
    exercises,
    masteryProfile: mastery,
    currentExerciseId: "EX010"
  });

  assert.equal(result.exercise?.id, "EX011");
  assert.equal(result.exactMatch, true);
});

test("falls back to the weakest KC when the request is unknown", () => {
  const result = recommendExercise({
    message: "Choose something useful",
    exercises,
    masteryProfile: mastery,
    currentExerciseId: "EX001"
  });

  assert.equal(result.exercise?.id, "EX010");
});

test("returns no exercise when no alternative exists", () => {
  const result = recommendExercise({
    message: "variables",
    exercises: [exercises[0]],
    masteryProfile: mastery,
    currentExerciseId: "EX001"
  });

  assert.equal(result.exercise, null);
});
