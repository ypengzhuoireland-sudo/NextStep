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
    let alive = true;

    async function load() {
      setLoadState("loading");
      try {
        const data = await getCurrentPracticeSession();
        if (!alive) {
          return;
        }
        setSession(data);
        setCode(data.exercise.starterCode);
        setLoadState("ready");
      } catch {
        if (alive) {
          setLoadState("error");
        }
      }
    }

    void load();

    return () => {
      alive = false;
    };
  }, []);

  const applySubmissionResult = useCallback((result: SubmissionResult) => {
    setSession((current) => {
      if (!current) {
        return current;
      }

      const nextProfile = current.masteryProfile.map((kc) => {
        const hit = result.masteryDelta.find((item) => item.kcCode === kc.code);
        if (!hit) {
          return kc;
        }
        const score = hit.after;
        const state: MasteryState =
          score >= 0.75
            ? "mastered"
            : score >= 0.6
              ? "almost_there"
              : "needs_practice";

        return {
          ...kc,
          mastery: score,
          trend: hit.after - hit.before,
          state
        };
      });

      return {
        ...current,
        latestResult: result,
        masteryProfile: nextProfile
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
      applySubmissionResult(result);
    } finally {
      setIsRunning(false);
    }
  }, [applySubmissionResult, code, session]);

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
      applySubmissionResult(result);
    } finally {
      setIsSubmitting(false);
    }
  }, [applySubmissionResult, code, session]);

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

        const exercise = {
          ...recommendation.exercise,
          recommendation: {
            strategy: recommendation.strategy,
            reason: recommendation.reason,
            confidence: recommendation.confidence
          }
        };

        return {
          ...current,
          exercise,
          latestResult: null,
          hintMessages: [],
          // TODO: keep old hint history somewhere once sessions are persisted
          learningPath: patchPathForNext(current.learningPath, exercise)
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

function patchPathForNext(items: LearningPathItem[], nextExercise: PracticeSession["exercise"]) {
  const alreadyQueued = items.find((item) => item.title === nextExercise.title);
  const nextItem: LearningPathItem = {
    id: alreadyQueued?.id ?? `path-${nextExercise.id}`,
    title: nextExercise.title,
    kcCode: nextExercise.kcTags[0]?.code ?? "python_basics",
    state: "current",
    etaMinutes: nextExercise.estimatedMinutes,
    difficulty: nextExercise.difficulty
  };

  const patched: LearningPathItem[] = [];
  for (const item of items) {
    if (item.state === "current") {
      patched.push({ ...item, state: "done" });
      continue;
    }
    if (item.title !== nextExercise.title) {
      if (item.state === "locked" || item.state === "done") {
        patched.push(item);
      } else {
        patched.push({ ...item, state: "queued" });
      }
    }
  }

  patched.splice(1, 0, nextItem);
  return patched.slice(0, 4);
}
