import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowLeft,
  BrainCircuit,
  CheckCircle2,
  LogOut,
  Loader2,
  Target
} from "lucide-react";
import { getStudentDashboardSummary } from "@/api/dashboard";
import { StatPill } from "@/components/common/StatPill";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { StudentDashboardSummary } from "@/types/tutor";
import { formatPercent } from "@/utils/formatters";

type DashboardLoadState = "idle" | "loading" | "ready" | "error";

interface StudentDashboardPageProps {
  onOpenPractice?: () => void;
  onLogout?: () => void;
}

export function StudentDashboardPage({ onOpenPractice, onLogout }: StudentDashboardPageProps) {
  const [summary, setSummary] = useState<StudentDashboardSummary | null>(null);
  const [loadState, setLoadState] = useState<DashboardLoadState>("idle");

  useEffect(() => {
    let isMounted = true;

    async function load() {
      setLoadState("loading");
      try {
        const data = await getStudentDashboardSummary();
        if (!isMounted) {
          return;
        }
        setSummary(data);
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

  const weakKcs = useMemo(
    () => [...(summary?.masteryProfile ?? [])].sort((a, b) => a.mastery - b.mastery).slice(0, 5),
    [summary?.masteryProfile]
  );

  if (loadState === "loading" || loadState === "idle") {
    return (
      <main className="soft-grid grid min-h-screen place-items-center p-6">
        <div className="glass-panel flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-slate-200">
          <Loader2 className="h-4 w-4 animate-spin text-cyan-200" />
          Loading student dashboard
        </div>
      </main>
    );
  }

  if (!summary || loadState === "error") {
    return (
      <main className="soft-grid grid min-h-screen place-items-center p-6">
        <div className="glass-panel max-w-md rounded-lg p-6 text-center">
          <div className="mx-auto grid h-12 w-12 place-items-center rounded-lg bg-rose-300/10">
            <AlertTriangle className="h-6 w-6 text-rose-100" />
          </div>
          <h1 className="mt-4 text-lg font-semibold text-white">Dashboard unavailable</h1>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            Your dashboard data could not be loaded. Check the API server or try again.
          </p>
          <Button className="mt-5" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </main>
    );
  }

  return (
    <main className="soft-grid min-h-screen overflow-x-hidden p-3 sm:p-5">
      <div className="mx-auto flex max-w-[1280px] flex-col gap-4">
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 border-b border-white/10 pb-4 lg:flex-row lg:items-center lg:justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-300/20 bg-cyan-300/10 shadow-glow">
              <BrainCircuit className="h-5 w-5 text-cyan-100" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-lg font-semibold text-white">Student Dashboard</h1>
                <Badge variant="blue">My Progress</Badge>
              </div>
              <p className="mt-1 text-xs text-slate-500">{summary.studentName}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onOpenPractice ? (
              <Button variant="secondary" onClick={onOpenPractice}>
                <ArrowLeft className="h-4 w-4" />
                Practice
              </Button>
            ) : null}
            {onLogout ? (
              <Button variant="ghost" onClick={onLogout}>
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            ) : null}
          </div>
        </motion.header>

        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="grid gap-3 md:grid-cols-3"
        >
          <StatPill icon={BrainCircuit} label="Average Mastery" value={formatPercent(summary.masteryAverage)} />
          <StatPill icon={Target} label="Weak KCs" value={String(weakKcs.length)} />
          <StatPill
            icon={CheckCircle2}
            label="Recommended"
            value={summary.recommendedExercise?.title ?? "None"}
          />
        </motion.section>

        <section className="grid gap-4 xl:grid-cols-[1fr_420px]">
          <Card>
            <CardHeader className="border-b border-white/10">
              <CardTitle>My KC Mastery</CardTitle>
              <Badge variant="default">{summary.masteryProfile.length} KCs</Badge>
            </CardHeader>
            <CardContent className="grid gap-3 p-4 md:grid-cols-2">
              {summary.masteryProfile.map((kc) => (
                <div key={kc.code} className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-white">{kc.name}</div>
                      <div className="mt-1 text-xs text-slate-500">{kc.code}</div>
                    </div>
                    <span className="font-mono text-sm text-slate-200">{formatPercent(kc.mastery)}</span>
                  </div>
                  <Progress className="mt-3" value={kc.mastery * 100} />
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="grid content-start gap-4">
            <Card>
              <CardHeader className="border-b border-white/10">
                <CardTitle>Next Step</CardTitle>
                <Badge variant="violet">adaptive</Badge>
              </CardHeader>
              <CardContent className="space-y-3 p-4">
                <p className="text-sm leading-6 text-slate-300">{summary.activeGoal}</p>
                {summary.recommendedExercise ? (
                  <div className="rounded-lg border border-violet-300/20 bg-violet-300/[0.08] p-3">
                    <div className="text-sm font-medium text-white">{summary.recommendedExercise.title}</div>
                    <div className="mt-1 text-xs text-slate-500">
                      {summary.recommendedExercise.primaryKc} / {summary.recommendedExercise.difficulty} /{" "}
                      {summary.recommendedExercise.estimatedMinutes} min
                    </div>
                  </div>
                ) : (
                  <div className="rounded-lg border border-white/10 bg-white/[0.04] p-3 text-sm text-slate-400">
                    No exercise recommendation is available yet.
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="border-b border-white/10">
                <CardTitle>Weak KC</CardTitle>
                <Badge variant="amber">review</Badge>
              </CardHeader>
              <CardContent className="space-y-3 p-4">
                {weakKcs.map((kc) => (
                  <div key={kc.code} className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-white">{kc.name}</div>
                        <div className="mt-1 text-xs text-slate-500">Needs practice</div>
                      </div>
                      <span className="font-mono text-xs text-slate-300">{formatPercent(kc.mastery)}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </main>
  );
}
