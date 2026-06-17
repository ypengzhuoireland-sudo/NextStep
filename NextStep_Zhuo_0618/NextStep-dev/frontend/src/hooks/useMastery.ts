import { useCallback, useEffect, useState } from "react";
import { getStudentMastery } from "@/api/mastery";
import type { StudentMasteryProfile } from "@/types/tutor";

type MasteryLoadState = "idle" | "loading" | "ready" | "error";

export function useMastery(studentId: string | null) {
  const [profile, setProfile] = useState<StudentMasteryProfile | null>(null);
  const [loadState, setLoadState] = useState<MasteryLoadState>("idle");

  const refetch = useCallback(async () => {
    if (!studentId) {
      setProfile(null);
      setLoadState("idle");
      return;
    }

    setLoadState("loading");
    try {
      const data = await getStudentMastery(studentId);
      setProfile(data);
      setLoadState("ready");
    } catch {
      setLoadState("error");
    }
  }, [studentId]);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  return {
    profile,
    loadState,
    isLoading: loadState === "loading",
    isError: loadState === "error",
    refetch
  };
}
