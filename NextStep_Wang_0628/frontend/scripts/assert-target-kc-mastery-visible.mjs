import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const practicePageSource = readFileSync(resolve(__dirname, "../src/pages/PracticePage.tsx"), "utf8");
const masteryWidgetSource = readFileSync(resolve(__dirname, "../src/components/mastery/MasteryWidget.tsx"), "utf8");
const practiceHookSource = readFileSync(resolve(__dirname, "../src/hooks/usePracticeSession.ts"), "utf8");

if (!practicePageSource.includes("targetKcs={session.exercise.kcTags}")) {
  throw new Error("PracticePage must pass current exercise KC tags into MasteryWidget.");
}

if (!masteryWidgetSource.includes("targetKcs: KnowledgeComponent[]")) {
  throw new Error("MasteryWidget props must accept targetKcs.");
}

if (!masteryWidgetSource.includes("Current Exercise KC")) {
  throw new Error("MasteryWidget must render a Current Exercise KC section.");
}

if (!practiceHookSource.includes("kcTags: current.exercise.kcTags.map")) {
  throw new Error("Submitting must update the current exercise KC tag mastery values.");
}

console.log("Current exercise KC mastery is visible and updated.");
