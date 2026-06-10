import { useCallback, useEffect, useMemo, useState } from "react";
import {
  getCurrentPracticeSession,
  getNextRecommendation,
  requestHint,
  runCode,
  submitCode
} from "@/api/tutor";
import type {
  HintMessage,
  LearningPathItem,
  MasteryState,
  PracticeSession,
  SubmissionResult
} from "@/types/tutor";

type LoadState = "idle" | "loading" | "ready" | "error";

export function usePracticeSession() {
  const [session, setSession] = useState<PracticeSession | null>(null);
  const [code, setCode] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isHinting, setIsHinting] = useState(false);
  const [isRecommending, setIsRecommending] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function load() {
      setLoadState("loading");
      try {
        const data = await getCurrentPracticeSession();
        if (!isMounted) {
          return;
        }
        setSession(data);
        setCode(data.exercise.starterCode);
        setLoadState("ready");
      } catch {
        if (isMounted) {
          setLoadState("error");
        }
      }
    }

    void load();

    return () => {
      isMounted = false;
    };
  }, []);

  const applyResult = useCallback((result: SubmissionResult) => {
    setSession((current) => {
      if (!current) {
        return current;
      }

      const masteryProfile = current.masteryProfile.map((kc) => {
        const delta = result.masteryDelta.find((item) => item.kcCode === kc.code);
        if (!delta) {
          return kc;
        }
        const nextMastery = delta.after;
        const nextState: MasteryState =
          nextMastery >= 0.75
            ? "mastered"
            : nextMastery >= 0.6
              ? "almost_there"
              : "needs_practice";

        return {
          ...kc,
          mastery: nextMastery,
          trend: delta.after - delta.before,
          state: nextState
        };
      });

      return {
        ...current,
        latestResult: result,
        masteryProfile
      };
    });
  }, []);

  const handleRun = useCallback(async () => {
    if (!session) {
      return;
    }

    setIsRunning(true);
    try {
      const result = await runCode({
        sessionId: session.sessionId,
        studentId: session.studentId,
        exerciseId: session.exercise.id,
        code
      });
      applyResult(result);
    } finally {
      setIsRunning(false);
    }
  }, [applyResult, code, session]);

  const handleSubmit = useCallback(async () => {
    if (!session) {
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await submitCode({
        sessionId: session.sessionId,
        studentId: session.studentId,
        exerciseId: session.exercise.id,
        code
      });
      applyResult(result);
    } finally {
      setIsSubmitting(false);
    }
  }, [applyResult, code, session]);

  const handleHint = useCallback(async (level: 1 | 2 | 3) => {
    if (!session) {
      return;
    }

    setIsHinting(true);
    try {
      const message = await requestHint({
        sessionId: session.sessionId,
        studentId: session.studentId,
        exerciseId: session.exercise.id,
        latestSubmissionId: session.latestResult?.id,
        requestedHintLevel: level
      });
      setSession((current) => {
        if (!current) {
          return current;
        }
        return {
          ...current,
          hintMessages: [...current.hintMessages, message]
        };
      });
    } finally {
      setIsHinting(false);
    }
  }, [session]);

  const handleNextExercise = useCallback(async () => {
    if (!session) {
      return;
    }

    setIsRecommending(true);
    try {
      const recommendation = await getNextRecommendation({
        sessionId: session.sessionId,
        studentId: session.studentId,
        currentExerciseId: session.exercise.id,
        strategy: session.experimentGroup,
        masteryProfile: session.masteryProfile
      });

      setSession((current) => {
        if (!current) {
          return current;
        }

        const nextExercise = {
          ...recommendation.exercise,
          recommendation: {
            strategy: recommendation.strategy,
            reason: recommendation.reason,
            confidence: recommendation.confidence
          }
        };

        return {
          ...current,
          exercise: nextExercise,
          latestResult: null,
          hintMessages: [],
          learningPath: buildNextLearningPath(current.learningPath, nextExercise)
        };
      });
      setCode(recommendation.exercise.starterCode);
    } finally {
      setIsRecommending(false);
    }
  }, [session]);

  const weakKcs = useMemo(() => {
    return [...(session?.masteryProfile ?? [])].sort((a, b) => a.mastery - b.mastery).slice(0, 4);
  }, [session?.masteryProfile]);

  const latestHint = useMemo<HintMessage | null>(() => {
    if (!session?.hintMessages.length) {
      return null;
    }
    return session.hintMessages[session.hintMessages.length - 1];
  }, [session?.hintMessages]);

  return {
    session,
    code,
    setCode,
    loadState,
    isRunning,
    isSubmitting,
    isHinting,
    isRecommending,
    weakKcs,
    latestHint,
    handleRun,
    handleSubmit,
    handleHint,
    handleNextExercise
  };
}

function buildNextLearningPath(
  items: LearningPathItem[],
  nextExercise: PracticeSession["exercise"]
): LearningPathItem[] {
  const existingNext = items.find((item) => item.title === nextExercise.title);
  const completed = items
    .filter((item) => item.state === "current")
    .map((item) => ({
      ...item,
      state: "done" as const
    }));

  const current: LearningPathItem = {
    id: existingNext?.id ?? `path-${nextExercise.id}`,
    title: nextExercise.title,
    kcCode: nextExercise.kcTags[0]?.code ?? "python_basics",
    state: "current",
    etaMinutes: nextExercise.estimatedMinutes,
    difficulty: nextExercise.difficulty
  };

  const queued = items
    .filter((item) => item.state !== "current" && item.title !== nextExercise.title)
    .map((item) => (item.state === "done" ? item : { ...item, state: item.state === "locked" ? item.state : "queued" as const }));

  return [...completed, current, ...queued].slice(0, 4);
}
