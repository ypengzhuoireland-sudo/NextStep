import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

function read(relativePath) {
  const absolutePath = path.join(root, relativePath);
  return fs.existsSync(absolutePath) ? fs.readFileSync(absolutePath, "utf8") : "";
}

const typeSource = read("src/types/tutor.ts");
const apiSource = read("src/api/learningAdvice.ts");
const tutorApiSource = read("src/api/tutor.ts");
const hookSource = read("src/hooks/usePracticeSession.ts");
const pageSource = read("src/pages/PracticePage.tsx");
const cardSource = read("src/components/mastery/LearningAdviceCard.tsx");

const checks = [
  {
    ok: typeSource.includes("export interface LearningAdvice"),
    message: "tutor.ts should define the LearningAdvice interface."
  },
  {
    ok: apiSource.includes("export async function getLearningAdvice"),
    message: "src/api/learningAdvice.ts should export getLearningAdvice()."
  },
  {
    ok: apiSource.includes("\"/learning-advice/student\""),
    message: "getLearningAdvice() should call /learning-advice/student."
  },
  {
    ok: tutorApiSource.includes("getLearningAdvice"),
    message: "src/api/tutor.ts should re-export getLearningAdvice."
  },
  {
    ok: cardSource.includes("AI Learning Advice"),
    message: "LearningAdviceCard should render an AI Learning Advice heading."
  },
  {
    ok: cardSource.includes("Next Steps"),
    message: "LearningAdviceCard should render next steps."
  },
  {
    ok: hookSource.includes("learningAdvice") && hookSource.includes("getLearningAdvice"),
    message: "usePracticeSession should load and expose learningAdvice."
  },
  {
    ok: hookSource.includes("refreshLearningAdvice"),
    message: "usePracticeSession should refresh learning advice after submissions."
  },
  {
    ok: pageSource.includes("<LearningAdviceCard") && pageSource.indexOf("<LearningAdviceCard") > pageSource.indexOf("<MasteryWidget"),
    message: "PracticePage should render LearningAdviceCard after MasteryWidget in the right sidebar."
  }
];

const failures = checks.filter((check) => !check.ok);

if (failures.length) {
  console.error(failures.map((failure) => `- ${failure.message}`).join("\n"));
  process.exit(1);
}

console.log("Learning Advice card is wired into the practice page.");
