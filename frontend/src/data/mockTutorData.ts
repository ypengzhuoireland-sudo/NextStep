import type {
  ClassDashboardSummary,
  Exercise,
  ExerciseListItem,
  KnowledgeComponent,
  PracticeSession,
  SubmissionResult
} from "@/types/tutor";

export const mockSession: PracticeSession = {
  sessionId: "ses_demo_20260605",
  studentId: "stu_python_beginner_01",
  experimentGroup: "adaptive",
  exercise: {
    id: "ex_lists_012",
    title: "Filter Passing Scores",
    slug: "filter-passing-scores",
    difficulty: "medium",
    estimatedMinutes: 14,
    prompt:
      "Write a function `passing_scores(scores)` that receives a list of integers and returns a new list containing only scores greater than or equal to 60. Keep the original order.",
    goal:
      "Practice list traversal, conditionals, and returning a transformed collection without mutating the input.",
    constraints: [
      "Use Python 3.11 syntax.",
      "Return a list, not a printed string.",
      "Do not change the original `scores` list.",
      "Hidden tests include empty lists and boundary score 60."
    ],
    examples: [
      {
        input: "passing_scores([88, 42, 60, 73])",
        output: "[88, 60, 73]",
        explanation: "42 is below the passing threshold; 60 should be included."
      },
      {
        input: "passing_scores([12, 55, 59])",
        output: "[]",
        explanation: "No score reaches 60, so the function returns an empty list."
      }
    ],
    starterCode:
      "def passing_scores(scores):\n    result = []\n    for score in scores:\n        # TODO: keep scores that pass\n        pass\n    return result\n",
    kcTags: [
      {
        code: "lists",
        name: "Lists",
        description: "List indexing, traversal, and basic access.",
        mastery: 0.46,
        trend: -0.06,
        state: "needs_practice"
      },
      {
        code: "conditionals",
        name: "Conditionals",
        description: "if / elif / else and boolean branches.",
        mastery: 0.71,
        trend: 0.04,
        state: "almost_there"
      },
      {
        code: "functions",
        name: "Functions",
        description: "Parameters, return values, and reusable logic.",
        mastery: 0.64,
        trend: 0.08,
        state: "almost_there"
      }
    ],
    recommendation: {
      strategy: "lowest_mastery_with_difficulty_match",
      reason:
        "Lists mastery is 0.46, below the 0.75 target. This medium exercise reinforces traversal while keeping conditionals familiar.",
      confidence: 0.86
    }
  },
  masteryProfile: [
    {
      code: "python_basics",
      name: "Python Basics",
      description: "print, input, variables, expressions.",
      mastery: 0.82,
      trend: 0.03,
      state: "mastered"
    },
    {
      code: "types_comparison",
      name: "Types",
      description: "int, float, str, bool, conversion, comparison.",
      mastery: 0.76,
      trend: 0.06,
      state: "mastered"
    },
    {
      code: "conditionals",
      name: "Conditionals",
      description: "Branching with if / elif / else.",
      mastery: 0.71,
      trend: 0.04,
      state: "almost_there"
    },
    {
      code: "loops",
      name: "Loops",
      description: "for, while, range, accumulators.",
      mastery: 0.58,
      trend: -0.02,
      state: "needs_practice"
    },
    {
      code: "lists",
      name: "Lists",
      description: "List creation, indexing, traversal.",
      mastery: 0.46,
      trend: -0.06,
      state: "needs_practice"
    },
    {
      code: "list_operations",
      name: "List Ops",
      description: "append, remove, sort, slicing.",
      mastery: 0.39,
      trend: 0.01,
      state: "needs_practice"
    },
    {
      code: "string_operations",
      name: "Strings",
      description: "split, join, slicing, cleaning text.",
      mastery: 0.68,
      trend: 0.05,
      state: "almost_there"
    },
    {
      code: "functions",
      name: "Functions",
      description: "Definitions, parameters, return values.",
      mastery: 0.64,
      trend: 0.08,
      state: "almost_there"
    },
    {
      code: "tuples_dicts_sets",
      name: "Dicts & Sets",
      description: "Key-value lookup, uniqueness, membership.",
      mastery: 0.44,
      trend: 0.02,
      state: "needs_practice"
    },
    {
      code: "exceptions",
      name: "Exceptions",
      description: "try / except, friendly error handling.",
      mastery: 0.31,
      trend: -0.04,
      state: "needs_practice"
    }
  ],
  learningPath: [
    {
      id: "path-1",
      title: "Filter Passing Scores",
      kcCode: "lists",
      state: "current",
      etaMinutes: 14,
      difficulty: "medium"
    },
    {
      id: "path-2",
      title: "Count Positive Values",
      kcCode: "loops",
      state: "queued",
      etaMinutes: 12,
      difficulty: "easy"
    },
    {
      id: "path-3",
      title: "Top Three Scores",
      kcCode: "list_operations",
      state: "queued",
      etaMinutes: 18,
      difficulty: "medium"
    },
    {
      id: "path-4",
      title: "Safe Integer Parser",
      kcCode: "exceptions",
      state: "locked",
      etaMinutes: 16,
      difficulty: "medium"
    }
  ],
  dashboardSeries: [
    { name: "Mon", mastery: 42, attempts: 6, hints: 3 },
    { name: "Tue", mastery: 48, attempts: 8, hints: 2 },
    { name: "Wed", mastery: 52, attempts: 11, hints: 4 },
    { name: "Thu", mastery: 57, attempts: 9, hints: 2 },
    { name: "Fri", mastery: 64, attempts: 13, hints: 3 },
    { name: "Sat", mastery: 67, attempts: 7, hints: 1 },
    { name: "Sun", mastery: 71, attempts: 10, hints: 2 }
  ],
  latestResult: null,
  hintMessages: [
    {
      id: "hint-1",
      role: "assistant",
      level: 1,
      title: "Start with the collection",
      text:
        "Your result list should grow only when a score satisfies the passing rule. Look for the one line inside the loop where that decision belongs.",
      kcCode: "lists",
      createdAt: "21:14"
    }
  ]
};

export const mockExerciseCatalog: Exercise[] = [
  mockSession.exercise,
  {
    id: "ex_loops_006",
    title: "Count Positive Values",
    slug: "count-positive-values",
    difficulty: "easy",
    estimatedMinutes: 12,
    prompt:
      "Write a function `count_positive(numbers)` that returns how many values in a list are greater than 0.",
    goal:
      "Practice looping through a list, maintaining a counter, and using a simple conditional.",
    constraints: [
      "Return an integer count.",
      "Use a loop or clear traversal logic.",
      "Zero is not positive.",
      "Hidden tests include empty lists and all-negative lists."
    ],
    examples: [
      {
        input: "count_positive([3, -1, 0, 8])",
        output: "2",
        explanation: "Only 3 and 8 are greater than 0."
      },
      {
        input: "count_positive([-5, 0, -2])",
        output: "0",
        explanation: "There are no positive values."
      }
    ],
    starterCode:
      "def count_positive(numbers):\n    count = 0\n    for number in numbers:\n        # TODO: count positive values\n        pass\n    return count\n",
    kcTags: kcs(["loops", "conditionals", "lists"]),
    recommendation: {
      strategy: "lowest_mastery_with_difficulty_match",
      reason:
        "Loops mastery is below the target threshold. This easy counter problem isolates traversal before adding more list operations.",
      confidence: 0.81
    }
  },
  {
    id: "ex_list_ops_018",
    title: "Top Three Scores",
    slug: "top-three-scores",
    difficulty: "medium",
    estimatedMinutes: 18,
    prompt:
      "Write a function `top_three(scores)` that returns a new list with the three highest scores in descending order. If there are fewer than three scores, return all of them sorted descending.",
    goal:
      "Practice sorting, slicing, and returning a new list without changing the input list.",
    constraints: [
      "Return a list.",
      "Do not mutate the original `scores` list.",
      "Sort highest to lowest.",
      "Hidden tests include duplicate scores and short lists."
    ],
    examples: [
      {
        input: "top_three([75, 92, 88, 92, 61])",
        output: "[92, 92, 88]",
        explanation: "The three largest values are kept in descending order."
      },
      {
        input: "top_three([70, 85])",
        output: "[85, 70]",
        explanation: "With fewer than three values, return every score sorted descending."
      }
    ],
    starterCode:
      "def top_three(scores):\n    ordered = list(scores)\n    # TODO: sort and keep the first three\n    return ordered\n",
    kcTags: kcs(["list_operations", "lists", "functions"]),
    recommendation: {
      strategy: "lowest_mastery_with_difficulty_match",
      reason:
        "List operations mastery is 0.39, the lowest active KC. This exercise targets sorting and slicing with familiar function structure.",
      confidence: 0.88
    }
  },
  {
    id: "ex_dicts_010",
    title: "Count Word Frequencies",
    slug: "count-word-frequencies",
    difficulty: "medium",
    estimatedMinutes: 16,
    prompt:
      "Write a function `word_counts(words)` that receives a list of strings and returns a dictionary mapping each word to how many times it appears.",
    goal:
      "Practice dictionary lookup, membership checks, and updating counts.",
    constraints: [
      "Return a dictionary.",
      "Keep words exactly as provided.",
      "Do not use Counter for this exercise.",
      "Hidden tests include repeated and empty input lists."
    ],
    examples: [
      {
        input: "word_counts(['red', 'blue', 'red'])",
        output: "{'red': 2, 'blue': 1}",
        explanation: "Each repeated word increments its existing count."
      }
    ],
    starterCode:
      "def word_counts(words):\n    counts = {}\n    for word in words:\n        # TODO: update the dictionary\n        pass\n    return counts\n",
    kcTags: kcs(["tuples_dicts_sets", "loops", "conditionals"]),
    recommendation: {
      strategy: "lowest_mastery_with_difficulty_match",
      reason:
        "Dictionary and set mastery is still fragile. This problem uses one repeated update pattern with light loop practice.",
      confidence: 0.79
    }
  },
  {
    id: "ex_exceptions_004",
    title: "Safe Integer Parser",
    slug: "safe-integer-parser",
    difficulty: "medium",
    estimatedMinutes: 16,
    prompt:
      "Write a function `safe_int(text)` that returns the integer value of a string, or returns `None` when the text cannot be parsed.",
    goal:
      "Practice try / except with a small, friendly error-handling function.",
    constraints: [
      "Return `None` for invalid input.",
      "Do not print error messages.",
      "Use `try` and `except ValueError`.",
      "Hidden tests include spaces, negative numbers, and words."
    ],
    examples: [
      {
        input: "safe_int('42')",
        output: "42",
        explanation: "A valid integer string should parse normally."
      },
      {
        input: "safe_int('hello')",
        output: "None",
        explanation: "Invalid integer text should not crash the program."
      }
    ],
    starterCode:
      "def safe_int(text):\n    # TODO: parse text safely\n    return None\n",
    kcTags: kcs(["exceptions", "types_comparison", "functions"]),
    recommendation: {
      strategy: "lowest_mastery_with_difficulty_match",
      reason:
        "Exceptions mastery is 0.31, well below the 0.75 target. This focused parser introduces recoverable errors without extra data structure work.",
      confidence: 0.9
    }
  }
];

export const mockExerciseList: ExerciseListItem[] = mockExerciseCatalog.map((exercise) => ({
  id: exercise.id,
  title: exercise.title,
  difficulty: exercise.difficulty,
  primaryKc: exercise.kcTags[0]?.code ?? "python_basics",
  estimatedMinutes: exercise.estimatedMinutes,
  status: "published"
}));

export const mockFailedSubmission: SubmissionResult = {
  id: "sub_demo_failed",
  status: "failed",
  summary: "2 of 4 tests passed. Boundary values around 60 need another look.",
  errorType: "failed_tests",
  runtimeMs: 43,
  memoryMb: 18.4,
  passedCount: 2,
  totalCount: 4,
  stdout: "Running pytest harness...\ncase_1 passed\ncase_2 failed\ncase_3 passed\ncase_4 failed",
  stderr:
    "AssertionError: expected [88, 60, 73], received [88, 73]\nHint: score == 60 is considered passing.",
  testCases: [
    {
      id: "case-1",
      label: "Mixed scores",
      input: "[88, 42, 73]",
      expected: "[88, 73]",
      actual: "[88, 73]",
      hidden: false,
      passed: true,
      runtimeMs: 9
    },
    {
      id: "case-2",
      label: "Boundary score",
      input: "[88, 42, 60, 73]",
      expected: "[88, 60, 73]",
      actual: "[88, 73]",
      hidden: false,
      passed: false,
      runtimeMs: 11
    },
    {
      id: "case-3",
      label: "No passing score",
      input: "[12, 55, 59]",
      expected: "[]",
      actual: "[]",
      hidden: false,
      passed: true,
      runtimeMs: 8
    },
    {
      id: "case-4",
      label: "Hidden empty and exact threshold",
      input: "hidden",
      expected: "hidden",
      actual: "hidden",
      hidden: true,
      passed: false,
      runtimeMs: 15
    }
  ],
  masteryDelta: [
    { kcCode: "lists", before: 0.46, after: 0.49 },
    { kcCode: "conditionals", before: 0.71, after: 0.69 },
    { kcCode: "functions", before: 0.64, after: 0.66 }
  ]
};

export const mockPassedSubmission: SubmissionResult = {
  ...mockFailedSubmission,
  id: "sub_demo_passed",
  status: "passed",
  summary: "All 4 tests passed. Nice recovery on the threshold case.",
  errorType: undefined,
  runtimeMs: 38,
  memoryMb: 18.1,
  passedCount: 4,
  stdout: "Running pytest harness...\ncase_1 passed\ncase_2 passed\ncase_3 passed\ncase_4 passed",
  stderr: "",
  testCases: mockFailedSubmission.testCases.map((testCase) => ({
    ...testCase,
    passed: true,
    actual: testCase.hidden ? "hidden" : testCase.expected
  })),
  masteryDelta: [
    { kcCode: "lists", before: 0.49, after: 0.57 },
    { kcCode: "conditionals", before: 0.69, after: 0.73 },
    { kcCode: "functions", before: 0.66, after: 0.7 }
  ]
};

export const mockClassDashboard: ClassDashboardSummary = {
  classId: "demo-python-101",
  updatedAt: "2026-06-06T10:30:00Z",
  totals: {
    students: 18,
    averageMastery: 0.63,
    submissions7d: 146,
    hintRequests7d: 52,
    atRiskCount: 4
  },
  heatmap: [
    ...dashRow("stu_python_beginner_01", "Mina Chen", [0.82, 0.76, 0.71, 0.58, 0.46, 0.39, 0.68, 0.64, 0.44, 0.31]),
    ...dashRow("stu_python_beginner_02", "Owen Patel", [0.74, 0.69, 0.52, 0.48, 0.57, 0.42, 0.62, 0.59, 0.38, 0.35]),
    ...dashRow("stu_python_beginner_03", "Ava Brooks", [
      0.88, 0.81, 0.78, 0.73, 0.69, 0.66, 0.72, 0.7, 0.55, 0.46
    ]),
    ...dashRow("stu_python_beginner_04", "Leo Gomez", [0.61, 0.58, 0.49, 0.43, 0.41, 0.33, 0.52, 0.48, 0.36, 0.29]),
    ...dashRow("stu_python_beginner_05", "Nora Smith", [0.79, 0.73, 0.67, 0.62, 0.55, 0.5, 0.71, 0.66, 0.49, 0.4])
  ],
  riskStudents: [
    {
      studentId: "stu_python_beginner_04",
      displayName: "Leo Gomez",
      averageMastery: 0.45,
      failedAttempts7d: 11,
      hintsUsed7d: 8,
      weakestKc: "exceptions",
      lastActiveAt: "Today 09:42"
    },
    {
      studentId: "stu_python_beginner_02",
      displayName: "Owen Patel",
      averageMastery: 0.54,
      failedAttempts7d: 8,
      hintsUsed7d: 7,
      weakestKc: "tuples_dicts_sets",
      lastActiveAt: "Today 09:18"
    },
    {
      studentId: "stu_python_beginner_01",
      displayName: "Mina Chen",
      averageMastery: 0.58,
      failedAttempts7d: 6,
      hintsUsed7d: 5,
      weakestKc: "exceptions",
      lastActiveAt: "Yesterday 21:14"
    }
  ],
  weakKcs: [
    {
      kcCode: "exceptions",
      kcName: "Exceptions",
      averageMastery: 0.36,
      affectedStudents: 12,
      trend: -0.04
    },
    {
      kcCode: "list_operations",
      kcName: "List Ops",
      averageMastery: 0.46,
      affectedStudents: 10,
      trend: 0.01
    },
    {
      kcCode: "tuples_dicts_sets",
      kcName: "Dicts & Sets",
      averageMastery: 0.44,
      affectedStudents: 9,
      trend: -0.01
    },
    {
      kcCode: "loops",
      kcName: "Loops",
      averageMastery: 0.57,
      affectedStudents: 7,
      trend: 0.03
    }
  ],
  recentSubmissions: [
    {
      id: "sub_recent_101",
      studentId: "stu_python_beginner_04",
      displayName: "Leo Gomez",
      exerciseTitle: "Safe Integer Parser",
      kcCode: "exceptions",
      status: "failed",
      passedCount: 2,
      totalCount: 5,
      runtimeMs: 61,
      createdAt: "10:24"
    },
    {
      id: "sub_recent_102",
      studentId: "stu_python_beginner_03",
      displayName: "Ava Brooks",
      exerciseTitle: "Top Three Scores",
      kcCode: "list_operations",
      status: "passed",
      passedCount: 6,
      totalCount: 6,
      runtimeMs: 44,
      createdAt: "10:19"
    },
    {
      id: "sub_recent_103",
      studentId: "stu_python_beginner_02",
      displayName: "Owen Patel",
      exerciseTitle: "Count Word Frequencies",
      kcCode: "tuples_dicts_sets",
      status: "failed",
      passedCount: 3,
      totalCount: 5,
      runtimeMs: 58,
      createdAt: "10:12"
    },
    {
      id: "sub_recent_104",
      studentId: "stu_python_beginner_01",
      displayName: "Mina Chen",
      exerciseTitle: "Filter Passing Scores",
      kcCode: "lists",
      status: "passed",
      passedCount: 4,
      totalCount: 4,
      runtimeMs: 38,
      createdAt: "10:05"
    }
  ]
};

function kcs(codes: string[]): KnowledgeComponent[] {
  return codes.map((code) => {
    const kc = mockSession.masteryProfile.find((item) => item.code === code);
    if (!kc) {
      throw new Error(`Unknown mock KC: ${code}`);
    }
    return { ...kc };
  });
}

function dashRow(studentId: string, displayName: string, masteryValues: number[]) {
  return mockSession.masteryProfile.map((kc, index) => ({
    studentId,
    displayName,
    kcCode: kc.code,
    kcName: kc.name,
    mastery: masteryValues[index] ?? kc.mastery
  }));
}
