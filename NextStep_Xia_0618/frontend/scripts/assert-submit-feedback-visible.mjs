import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const practicePageSource = readFileSync(resolve(__dirname, "../src/pages/PracticePage.tsx"), "utf8");
const codeEditorSource = readFileSync(resolve(__dirname, "../src/components/exercise/CodeEditor.tsx"), "utf8");

if (!practicePageSource.includes("latestResult={session.latestResult}")) {
  throw new Error("PracticePage must pass session.latestResult into CodeEditor.");
}

if (!codeEditorSource.includes("latestResult: SubmissionResult | null")) {
  throw new Error("CodeEditor props must accept latestResult.");
}

if (!codeEditorSource.includes("Last result")) {
  throw new Error("CodeEditor must render a visible last submission result summary.");
}

console.log("Submit feedback is visible in the editor area.");
