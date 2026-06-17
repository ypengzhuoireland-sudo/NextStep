import assert from "node:assert/strict";
import test from "node:test";

import {
  buildAssistantChatPayload,
  mapAssistantChatResponse
} from "../src/features/studyAssistant/assistantApiProtocol.ts";


test("builds the backend assistant request body", () => {
  assert.deepEqual(
    buildAssistantChatPayload(
      "  I want a hard loops exercise  ",
      "EX001"
    ),
    {
      message: "I want a hard loops exercise",
      currentExerciseId: "EX001"
    }
  );
});


test("maps the backend response to the dialog recommendation shape", () => {
  const result = mapAssistantChatResponse({
    message: "This exercise matches the topic you requested.",
    intent: {
      kcCode: "KC003",
      difficulty: "easy",
      useWeakestKc: false,
      source: "openai"
    },
    recommendedExercise: {
      id: "EX003",
      title: "Loop Practice",
      difficulty: "easy",
      primaryKc: "KC003",
      estimatedMinutes: 6,
      status: "published"
    },
    exactMatch: true
  });

  assert.equal(result.exercise?.id, "EX003");
  assert.equal(result.reason, "This exercise matches the topic you requested.");
  assert.equal(result.intentSource, "openai");
  assert.equal(result.exactMatch, true);
});
