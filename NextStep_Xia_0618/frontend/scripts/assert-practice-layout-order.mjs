import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const practicePagePath = resolve(__dirname, "../src/pages/PracticePage.tsx");
const source = readFileSync(practicePagePath, "utf8");

const nextExerciseIndex = source.indexOf("<NextExerciseButton");
const masteryIndex = source.indexOf("<MasteryWidget");
const hintIndex = source.indexOf("<HintPanel");

if (nextExerciseIndex === -1 || masteryIndex === -1 || hintIndex === -1) {
  throw new Error("Practice sidebar is missing NextExerciseButton, MasteryWidget, or HintPanel.");
}

if (!(nextExerciseIndex < masteryIndex && masteryIndex < hintIndex)) {
  throw new Error("Expected sidebar order: NextExerciseButton, MasteryWidget, HintPanel.");
}

console.log("Practice sidebar order is correct.");
