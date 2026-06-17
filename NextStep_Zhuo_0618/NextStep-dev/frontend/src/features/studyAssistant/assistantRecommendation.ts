export type AssistantDifficulty = "easy" | "medium" | "hard";

export interface AssistantIntent {
  kcCode: string | null;
  difficulty: AssistantDifficulty | null;
  useWeakestKc: boolean;
}

export interface AssistantExercise {
  id: string;
  title: string;
  difficulty: AssistantDifficulty;
  primaryKc: string;
  estimatedMinutes: number;
  status: "published" | "draft";
}

export interface AssistantMastery {
  code: string;
  mastery: number;
}

export interface RecommendationResult {
  exercise: AssistantExercise | null;
  intent: AssistantIntent;
  exactMatch: boolean;
  reason: string;
}

interface RecommendationArgs {
  message: string;
  exercises: AssistantExercise[];
  masteryProfile: AssistantMastery[];
  currentExerciseId: string;
}

const KC_ALIASES: Array<[string, string[]]> = [
  ["KC001", ["variable", "variables", "expression", "expressions", "basic", "basics"]],
  ["KC002", ["condition", "conditions", "conditional", "conditionals", "if", "else"]],
  ["KC003", ["loop", "loops", "for loop", "while loop", "iteration"]],
  ["KC004", ["function", "functions", "parameter", "parameters", "return value"]],
  ["KC005", ["string", "strings", "text"]],
  ["KC006", ["list", "lists", "array", "arrays"]],
  ["KC007", ["dictionary", "dictionaries", "dict", "set", "sets"]],
  ["KC008", ["nested data", "nested list", "nested lists", "nested structure"]],
  ["KC009", ["recursion", "recursive"]],
  ["KC010", ["oop", "object oriented", "object-oriented", "class", "classes", "object", "objects"]],
  ["KC011", ["exception", "exceptions", "error handling", "validation", "try except"]],
  ["KC012", ["algorithm", "algorithms", "problem solving", "problem-solving"]]
];

const DIFFICULTY_ALIASES: Array<[AssistantDifficulty, string[]]> = [
  ["easy", ["easy", "easier", "beginner", "simple", "basic"]],
  ["medium", ["medium", "intermediate", "normal"]],
  ["hard", ["hard", "harder", "advanced", "difficult", "challenging"]]
];

const WEAKEST_PATTERNS = [
  "weak topic",
  "weakest",
  "weak area",
  "what should i practise",
  "what should i practice",
  "recommend something",
  "choose something",
  "something useful"
];

export function parseAssistantIntent(message: string): AssistantIntent {
  const normalized = normalize(message);
  const kcCode =
    KC_ALIASES.find(([, aliases]) =>
      aliases.some((alias) => containsPhrase(normalized, alias))
    )?.[0] ?? null;
  const difficulty =
    DIFFICULTY_ALIASES.find(([, aliases]) =>
      aliases.some((alias) => containsPhrase(normalized, alias))
    )?.[0] ?? null;
  const useWeakestKc =
    kcCode === null ||
    WEAKEST_PATTERNS.some((pattern) => normalized.includes(pattern));

  return {
    kcCode,
    difficulty,
    useWeakestKc
  };
}

export function recommendExercise({
  message,
  exercises,
  masteryProfile,
  currentExerciseId
}: RecommendationArgs): RecommendationResult {
  const intent = parseAssistantIntent(message);
  const available = exercises.filter(
    (exercise) =>
      exercise.status === "published" &&
      exercise.id !== currentExerciseId
  );

  if (available.length === 0) {
    return {
      exercise: null,
      intent,
      exactMatch: false,
      reason: "No other published exercise is available."
    };
  }

  const weakestKc = [...masteryProfile]
    .sort((left, right) =>
      left.mastery === right.mastery
        ? left.code.localeCompare(right.code)
        : left.mastery - right.mastery
    )[0]?.code ?? null;
  const targetKc =
    intent.kcCode ?? (intent.useWeakestKc ? weakestKc : null);
  const masteryByKc = new Map(
    masteryProfile.map((item) => [item.code, item.mastery])
  );
  const ranked = [...available].sort((left, right) => {
    const scoreDifference =
      scoreExercise(right, targetKc, intent.difficulty, masteryByKc) -
      scoreExercise(left, targetKc, intent.difficulty, masteryByKc);

    return scoreDifference || left.id.localeCompare(right.id);
  });
  const exercise = ranked[0];
  const exactMatch =
    (!targetKc || exercise.primaryKc === targetKc) &&
    (!intent.difficulty || exercise.difficulty === intent.difficulty);

  return {
    exercise,
    intent,
    exactMatch,
    reason: buildReason(exercise, targetKc, intent.difficulty, exactMatch)
  };
}

function scoreExercise(
  exercise: AssistantExercise,
  targetKc: string | null,
  difficulty: AssistantDifficulty | null,
  masteryByKc: Map<string, number>
): number {
  let score = 0;

  if (targetKc && exercise.primaryKc === targetKc) {
    score += 100;
  }
  if (difficulty && exercise.difficulty === difficulty) {
    score += 30;
  }

  score += (1 - (masteryByKc.get(exercise.primaryKc) ?? 0)) * 10;
  return score;
}

function buildReason(
  exercise: AssistantExercise,
  targetKc: string | null,
  difficulty: AssistantDifficulty | null,
  exactMatch: boolean
): string {
  if (!exactMatch) {
    return "I could not find an exact match, so I selected the closest available exercise.";
  }
  if (targetKc && difficulty) {
    return `This ${exercise.difficulty} exercise matches the topic and difficulty you requested.`;
  }
  if (targetKc) {
    return "This exercise matches the topic you requested.";
  }

  return "This exercise targets one of your lowest-mastery knowledge areas.";
}

function normalize(value: string): string {
  return value.toLowerCase().replace(/[^\p{L}\p{N}-]+/gu, " ").trim();
}

function containsPhrase(value: string, phrase: string): boolean {
  return ` ${value} `.includes(` ${phrase} `);
}
