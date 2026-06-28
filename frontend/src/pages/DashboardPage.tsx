import { Fragment, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowLeft,
  ArrowUpRight,
  BrainCircuit,
  Clock3,
  GraduationCap,
  Loader2,
  MessageSquareText,
  UsersRound
} from "lucide-react";
import { getClassDashboardSummary } from "@/api/dashboard";
import { StatPill } from "@/components/common/StatPill";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { ClassDashboardSummary, ExecutionStatus } from "@/types/tutor";
import { formatPercent, heatmapColor } from "@/utils/formatters";

type DashboardLoadState = "idle" | "loading" | "ready" | "error";

interface DashboardPageProps {
  onOpenPractice?: () => void;
}

export function DashboardPage({ onOpenPractice }: DashboardPageProps) {
  const [summary, setSummary] = useState<ClassDashboardSummary | null>(null);
  const [loadState, setLoadState] = useState<DashboardLoadState>("idle");

  useEffect(() => {
    let isMounted = true;

    async function load() {
      setLoadState("loading");
      try {
        const data = await getClassDashboardSummary();
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

  const heatmapModel = useMemo(() => {
    const cells = summary?.heatmap ?? [];
    const students = Array.from(
      new Map(cells.map((cell) => [cell.studentId, cell.displayName])).entries()
    ).map(([studentId, displayName]) => ({ studentId, displayName }));
    const kcs = Array.from(
      new Map(
        cells.map((cell) => [
          cell.kcCode,
          {
            kcCode: cell.kcCode,
            kcName: cell.kcName,
            kcShortName: cell.kcShortName
          }
        ])
      ).values()
    );

    return {
      students,
      kcs,
      getCell: (studentId: string, kcCode: string) =>
        cells.find((cell) => cell.studentId === studentId && cell.kcCode === kcCode)
    };
  }, [summary?.heatmap]);

  if (loadState === "loading" || loadState === "idle") {
    return (
      <main className="soft-grid grid min-h-screen place-items-center p-6">
        <div className="glass-panel flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-slate-200">
          <Loader2 className="h-4 w-4 animate-spin text-cyan-200" />
          Loading class dashboard
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
            Class summary data could not be loaded. Check the API server or try again.
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
      <div className="mx-auto flex max-w-[1680px] flex-col gap-4">
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 border-b border-white/10 pb-4 lg:flex-row lg:items-center lg:justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-300/20 bg-cyan-300/10 shadow-glow">
              <GraduationCap className="h-5 w-5 text-cyan-100" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-lg font-semibold text-white">Teacher Dashboard</h1>
                <Badge variant="blue">{summary.classId}</Badge>
              </div>
              <p className="mt-1 text-xs text-slate-500">Updated {summary.updatedAt}</p>
            </div>
          </div>

          {onOpenPractice ? (
            <Button variant="secondary" onClick={onOpenPractice}>
              <ArrowLeft className="h-4 w-4" />
              Student Practice
            </Button>
          ) : null}
        </motion.header>

        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5"
        >
          <StatPill icon={UsersRound} label="Students" value={String(summary.totals.students)} />
          <StatPill icon={BrainCircuit} label="Avg Mastery" value={formatPercent(summary.totals.averageMastery)} />
          <StatPill icon={Activity} label="Submissions" value={String(summary.totals.submissions7d)} />
          <StatPill icon={MessageSquareText} label="Hints" value={String(summary.totals.hintRequests7d)} />
          <StatPill icon={AlertTriangle} label="At Risk" value={String(summary.totals.atRiskCount)} />
        </motion.section>

        <section className="grid gap-4 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.55fr)]">
          <Card className="min-w-0 overflow-hidden">
            <CardHeader className="border-b border-white/10">
              <div>
                <CardTitle>Class KC Heatmap</CardTitle>
                <p className="mt-1 text-xs text-slate-500">Rows are students; columns are knowledge components</p>
              </div>
              <Badge variant="default">{heatmapModel.students.length} shown</Badge>
            </CardHeader>

            <CardContent className="overflow-x-auto p-4">
              <div
                className="grid min-w-[860px] gap-2"
                style={{ gridTemplateColumns: `160px repeat(${heatmapModel.kcs.length}, minmax(54px, 1fr))` }}
              >
                <div className="h-10" />
                {heatmapModel.kcs.map((kc) => (
                  <div
                    key={kc.kcCode}
                    title={`${kc.kcCode} · ${kc.kcName}`}
                    className="flex h-10 items-end justify-center truncate px-1 text-center text-[10px] uppercase text-slate-500"
                  >
                    {kc.kcShortName ?? kc.kcName ?? kc.kcCode}
                  </div>
                ))}

                {heatmapModel.students.map((student) => (
                  <Fragment key={student.studentId}>
                    <div className="flex h-12 min-w-0 items-center rounded-lg border border-white/10 bg-white/[0.035] px-3">
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-white">{student.displayName}</div>
                        <div className="mt-0.5 truncate text-[10px] text-slate-500">{student.studentId}</div>
                      </div>
                    </div>
                    {heatmapModel.kcs.map((kc) => {
                      const cell = heatmapModel.getCell(student.studentId, kc.kcCode);
                      return (
                        <div
                          key={`${student.studentId}-${kc.kcCode}`}
                          title={`${student.displayName} / ${kc.kcName}: ${formatPercent(cell?.mastery ?? 0)}`}
                          className="grid h-12 place-items-center rounded-lg border border-white/10 bg-white/[0.035] p-1"
                        >
                          <div
                            className={`grid h-full w-full place-items-center rounded-md ${heatmapColor(cell?.mastery ?? 0)}`}
                          >
                            <span className="font-mono text-[10px] text-slate-950">
                              {Math.round((cell?.mastery ?? 0) * 100)}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </Fragment>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b border-white/10">
              <CardTitle>Low Mastery Students</CardTitle>
              <Badge variant="rose">{summary.riskStudents.length}</Badge>
            </CardHeader>
            <CardContent className="space-y-3 p-4">
              {summary.riskStudents.map((student) => (
                <div key={student.studentId} className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-white">{student.displayName}</div>
                      <div className="mt-1 text-xs text-slate-500">{student.weakestKc}</div>
                    </div>
                    <Badge variant={student.averageMastery < 0.5 ? "rose" : "amber"}>
                      {formatPercent(student.averageMastery)}
                    </Badge>
                  </div>
                  <Progress className="mt-3" value={student.averageMastery * 100} />
                  <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-slate-400">
                    <MiniMetric label="Failed" value={student.failedAttempts7d} />
                    <MiniMetric label="Hints" value={student.hintsUsed7d} />
                    <MiniMetric label="Active" value={student.lastActiveAt} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <Card>
            <CardHeader className="border-b border-white/10">
              <CardTitle>Weak KC Summary</CardTitle>
              <Badge variant="amber">below target</Badge>
            </CardHeader>
            <CardContent className="space-y-3 p-4">
              {summary.weakKcs.map((kc) => {
                const TrendIcon = kc.trend >= 0 ? ArrowUpRight : ArrowDownRight;
                return (
                  <div key={kc.kcCode} className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-white">{kc.kcName}</div>
                        <div className="mt-1 text-xs text-slate-500">
                          {kc.affectedStudents} students affected
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendIcon className={kc.trend >= 0 ? "h-4 w-4 text-emerald-200" : "h-4 w-4 text-rose-200"} />
                        <span className="font-mono text-xs text-slate-300">
                          {kc.trend >= 0 ? "+" : ""}
                          {Math.round(kc.trend * 100)}
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 flex items-center gap-3">
                      <Progress className="flex-1" value={kc.averageMastery * 100} />
                      <span className="font-mono text-xs text-slate-200">{formatPercent(kc.averageMastery)}</span>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b border-white/10">
              <CardTitle>Recent Submissions</CardTitle>
              <Badge variant="default">live mock</Badge>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-white/10">
                {summary.recentSubmissions.map((submission) => (
                  <div
                    key={submission.id}
                    className="grid gap-3 px-4 py-3 md:grid-cols-[1fr_160px_120px_80px]"
                  >
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-white">{submission.exerciseTitle}</div>
                      <div className="mt-1 truncate text-xs text-slate-500">
                        {submission.displayName} / {submission.kcCode}
                      </div>
                    </div>
                    <Badge className="w-fit" variant={statusVariant(submission.status)}>
                      {submission.status}
                    </Badge>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Activity className="h-3.5 w-3.5" />
                      {submission.passedCount}/{submission.totalCount} tests
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Clock3 className="h-3.5 w-3.5" />
                      {submission.createdAt}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}

function MiniMetric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="min-w-0 rounded-lg border border-white/10 bg-slate-950/25 px-2 py-2">
      <div className="truncate text-[10px] uppercase text-slate-500">{label}</div>
      <div className="mt-1 truncate text-xs font-semibold text-slate-100">{value}</div>
    </div>
  );
}

function statusVariant(status: ExecutionStatus) {
  if (status === "passed") {
    return "green";
  }

  if (status === "failed" || status === "error") {
    return "rose";
  }

  return "amber";
}
/* df */