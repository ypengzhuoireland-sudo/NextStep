import { Fragment, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BrainCircuit,
  ChevronRight,
  Clock3,
  GraduationCap,
  LogOut,
  Loader2,
  MessageSquareText,
  Search,
  UsersRound,
  X
} from "lucide-react";
import {
  getClassDashboardSummary,
  getClassStudentDetail,
  getClassStudentDirectory
} from "@/api/dashboard";
import { StatPill } from "@/components/common/StatPill";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type {
  ClassDashboardSummary,
  ClassStudentDetail,
  ClassStudentDirectory,
  ExecutionStatus
} from "@/types/tutor";
import { formatPercent, heatmapColor } from "@/utils/formatters";

type DashboardLoadState = "idle" | "loading" | "ready" | "error";

interface TeacherDashboardPageProps {
  onLogout?: () => void;
}

export function TeacherDashboardPage({ onLogout }: TeacherDashboardPageProps) {
  const [summary, setSummary] = useState<ClassDashboardSummary | null>(null);
  const [loadState, setLoadState] = useState<DashboardLoadState>("idle");
  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<"all" | "at_risk">("all");
  const [sortBy, setSortBy] = useState<"risk" | "name" | "recent">("risk");
  const [directory, setDirectory] = useState<ClassStudentDirectory | null>(null);
  const [isDirectoryOpen, setIsDirectoryOpen] = useState(false);
  const [isDirectoryLoading, setIsDirectoryLoading] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<ClassStudentDetail | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

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

  useEffect(() => {
    if (!summary || !isDirectoryOpen) {
      return;
    }
    let isMounted = true;
    const timer = window.setTimeout(async () => {
      setIsDirectoryLoading(true);
      try {
        const result = await getClassStudentDirectory(summary.classId, {
          query: searchQuery,
          risk: riskFilter,
          sort: sortBy,
          limit: 20
        });
        if (isMounted) {
          setDirectory(result);
        }
      } finally {
        if (isMounted) {
          setIsDirectoryLoading(false);
        }
      }
    }, 180);

    return () => {
      isMounted = false;
      window.clearTimeout(timer);
    };
  }, [isDirectoryOpen, riskFilter, searchQuery, sortBy, summary]);

  const openStudentDetail = useCallback(async (studentId: string) => {
    if (!summary) {
      return;
    }
    setIsDirectoryOpen(false);
    setSelectedStudent(null);
    setDetailError(null);
    setIsDetailLoading(true);
    try {
      const detail = await getClassStudentDetail(summary.classId, studentId);
      setSelectedStudent(detail);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Student details could not be loaded.");
    } finally {
      setIsDetailLoading(false);
    }
  }, [summary]);

  useEffect(() => {
    function handleSearchShortcut(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setIsDirectoryOpen(true);
        searchInputRef.current?.focus();
      }
    }

    window.addEventListener("keydown", handleSearchShortcut);
    return () => window.removeEventListener("keydown", handleSearchShortcut);
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
                <Badge variant="blue">{formatClassLabel(summary.classId)}</Badge>
              </div>
              <p className="mt-1 text-xs text-slate-500">Last updated: {formatDashboardTime(summary.updatedAt)}</p>
            </div>
          </div>

          {onLogout ? (
            <Button variant="secondary" onClick={onLogout}>
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          ) : null}
        </motion.header>

        <section className="relative z-20">
          <div className="flex flex-col gap-2 rounded-lg border border-white/10 bg-slate-950/30 p-3 lg:flex-row lg:items-center">
            <div className="relative min-w-0 flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input
                ref={searchInputRef}
                aria-label="Search students"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                onFocus={() => setIsDirectoryOpen(true)}
                onKeyDown={(event) => {
                  if (event.key === "Escape") {
                    setIsDirectoryOpen(false);
                  }
                }}
                placeholder="Search by student name or ID"
                className="h-10 w-full rounded-lg border border-white/10 bg-slate-950/50 pl-10 pr-10 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300/50 focus:ring-2 focus:ring-cyan-300/15"
              />
              {searchQuery ? (
                <button
                  type="button"
                  aria-label="Clear student search"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2 top-1/2 grid h-7 w-7 -translate-y-1/2 place-items-center rounded-md text-slate-400 hover:bg-white/[0.08] hover:text-white"
                >
                  <X className="h-4 w-4" />
                </button>
              ) : null}
            </div>
            <div className="grid grid-cols-2 gap-2 sm:flex">
              <select
                aria-label="Filter student risk"
                value={riskFilter}
                onChange={(event) => {
                  setRiskFilter(event.target.value as "all" | "at_risk");
                  setIsDirectoryOpen(true);
                }}
                className="h-10 rounded-lg border border-white/10 bg-slate-950/50 px-3 text-sm text-slate-200 outline-none focus:border-cyan-300/50"
              >
                <option value="all">All students</option>
                <option value="at_risk">At risk</option>
              </select>
              <select
                aria-label="Sort students"
                value={sortBy}
                onChange={(event) => {
                  setSortBy(event.target.value as "risk" | "name" | "recent");
                  setIsDirectoryOpen(true);
                }}
                className="h-10 rounded-lg border border-white/10 bg-slate-950/50 px-3 text-sm text-slate-200 outline-none focus:border-cyan-300/50"
              >
                <option value="risk">Lowest mastery</option>
                <option value="name">Name</option>
                <option value="recent">Least recent activity</option>
              </select>
            </div>
          </div>

          {isDirectoryOpen ? (
            <div className="absolute left-0 right-0 top-[calc(100%+0.5rem)] max-h-[420px] overflow-y-auto rounded-lg border border-white/10 bg-slate-950 shadow-2xl shadow-black/50">
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 text-xs text-slate-400">
                <span>{directory ? `${directory.total} students found` : "Searching students"}</span>
                {isDirectoryLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-200" /> : null}
              </div>
              {directory?.items.length ? (
                <div className="p-2">
                  {directory.items.map((student) => (
                    <button
                      key={student.studentId}
                      type="button"
                      onClick={() => void openStudentDetail(student.studentId)}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left transition-colors hover:bg-white/[0.07]"
                    >
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-sm font-medium text-white">{student.displayName}</div>
                        <div className="mt-1 truncate text-xs text-slate-500">{student.studentId} · {student.weakestKc}</div>
                      </div>
                      <Badge variant={student.riskLevel === "at_risk" ? "rose" : "green"}>
                        {formatPercent(student.averageMastery)}
                      </Badge>
                      <ChevronRight className="h-4 w-4 text-slate-500" />
                    </button>
                  ))}
                </div>
              ) : !isDirectoryLoading ? (
                <div className="px-4 py-8 text-center text-sm text-slate-400">No students match the current search.</div>
              ) : null}
            </div>
          ) : null}
        </section>

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
          <Card className="min-w-0 overflow-hidden xl:flex xl:h-[680px] xl:flex-col">
            <CardHeader className="border-b border-white/10">
              <div>
                <CardTitle>Class KC Heatmap</CardTitle>
                <p className="mt-1 text-xs text-slate-500">Rows are students; columns are knowledge components</p>
              </div>
              <Badge variant="default">{heatmapModel.students.length} shown</Badge>
            </CardHeader>

            <CardContent className="max-h-[620px] overflow-auto p-4 xl:min-h-0 xl:max-h-none xl:flex-1">
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
                    <button
                      type="button"
                      onClick={() => void openStudentDetail(student.studentId)}
                      className="flex h-12 min-w-0 items-center rounded-lg border border-white/10 bg-white/[0.035] px-3 text-left transition-colors hover:border-cyan-300/30 hover:bg-cyan-300/[0.06]"
                    >
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-white">{student.displayName}</div>
                        <div className="mt-0.5 truncate text-[10px] text-slate-500">{student.studentId}</div>
                      </div>
                    </button>
                    {heatmapModel.kcs.map((kc) => {
                      const cell = heatmapModel.getCell(student.studentId, kc.kcCode);
                      return (
                        <button
                          type="button"
                          onClick={() => void openStudentDetail(student.studentId)}
                          key={`${student.studentId}-${kc.kcCode}`}
                          title={`${student.displayName} / ${kc.kcName}: ${formatPercent(cell?.mastery ?? 0)}`}
                          className="grid h-12 place-items-center rounded-lg border border-white/10 bg-white/[0.035] p-1 transition-colors hover:border-cyan-300/30"
                        >
                          <div
                            className={`grid h-full w-full place-items-center rounded-md ${heatmapColor(cell?.mastery ?? 0)}`}
                          >
                            <span className="font-mono text-[10px] text-slate-950">
                              {Math.round((cell?.mastery ?? 0) * 100)}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </Fragment>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="overflow-hidden xl:flex xl:h-[680px] xl:flex-col">
            <CardHeader className="border-b border-white/10">
              <CardTitle>Low Mastery Students</CardTitle>
              <Badge variant="rose">{summary.riskStudents.length}</Badge>
            </CardHeader>
            <CardContent className="max-h-[620px] space-y-3 overflow-y-auto overscroll-contain p-4 xl:min-h-0 xl:max-h-none xl:flex-1">
              {summary.riskStudents.map((student) => (
                <button
                  key={student.studentId}
                  type="button"
                  onClick={() => void openStudentDetail(student.studentId)}
                  className="w-full rounded-lg border border-white/10 bg-white/[0.04] p-3 text-left transition-colors hover:border-cyan-300/30 hover:bg-cyan-300/[0.05]"
                >
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
                </button>
              ))}
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <Card className="overflow-hidden xl:flex xl:h-[620px] xl:flex-col">
            <CardHeader className="border-b border-white/10">
              <CardTitle>Weak KC Summary</CardTitle>
              <Badge variant="amber">below target</Badge>
            </CardHeader>
            <CardContent className="max-h-[560px] space-y-3 overflow-y-auto overscroll-contain p-4 xl:min-h-0 xl:max-h-none xl:flex-1">
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

          <Card className="overflow-hidden xl:flex xl:h-[620px] xl:flex-col">
            <CardHeader className="border-b border-white/10">
              <CardTitle>Recent Submissions</CardTitle>
              <Badge variant="default">from database</Badge>
            </CardHeader>
            <CardContent className="max-h-[560px] overflow-y-auto overscroll-contain p-0 xl:min-h-0 xl:max-h-none xl:flex-1">
              {summary.recentSubmissions.length > 0 ? (
                <div className="divide-y divide-white/10">
                  {summary.recentSubmissions.map((submission) => (
                    <button
                      type="button"
                      onClick={() => void openStudentDetail(submission.studentId)}
                      key={submission.id}
                      className="grid w-full gap-3 px-4 py-3 text-left transition-colors hover:bg-white/[0.035] md:grid-cols-[1fr_160px_120px_80px]"
                    >
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-white">{submission.exerciseTitle}</div>
                        <div className="mt-1 truncate text-xs text-slate-500">
                          Submitted by {submission.displayName}
                        </div>
                        <div className="mt-0.5 truncate text-[11px] text-slate-600">
                          {submission.kcCode}
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
                    </button>
                  ))}
                </div>
              ) : (
                <div className="px-4 py-6 text-sm leading-6 text-slate-400">
                  No saved submissions yet. Run Code only checks code; Submit creates records for this panel.
                </div>
              )}
            </CardContent>
          </Card>
        </section>
      </div>
      {(isDetailLoading || selectedStudent || detailError) ? (
        <StudentDetailDrawer
          detail={selectedStudent}
          error={detailError}
          loading={isDetailLoading}
          onClose={() => {
            setSelectedStudent(null);
            setDetailError(null);
          }}
        />
      ) : null}
    </main>
  );
}

function StudentDetailDrawer({
  detail,
  error,
  loading,
  onClose
}: {
  detail: ClassStudentDetail | null;
  error: string | null;
  loading: boolean;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/55 backdrop-blur-[1px]" role="dialog" aria-modal="true" aria-label="Student details">
      <section className="flex h-full w-full max-w-[520px] flex-col overflow-y-auto border-l border-white/10 bg-slate-950 shadow-2xl shadow-black/50">
        <header className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-white/10 bg-slate-950/95 px-5 py-4 backdrop-blur">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Student detail</p>
            <h2 className="mt-1 text-lg font-semibold text-white">{detail?.student.displayName ?? "Loading student"}</h2>
          </div>
          <Button size="icon" variant="ghost" onClick={onClose} aria-label="Close student details">
            <X className="h-4 w-4" />
          </Button>
        </header>

        {loading ? (
          <div className="grid flex-1 place-items-center p-8 text-sm text-slate-400">
            <span className="flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin text-cyan-200" /> Loading student details</span>
          </div>
        ) : error ? (
          <div className="p-5 text-sm text-rose-200">{error}</div>
        ) : detail ? (
          <div className="space-y-5 p-5">
            <div className="grid grid-cols-3 gap-3">
              <MiniMetric label="Mastery" value={formatPercent(detail.student.averageMastery)} />
              <MiniMetric label="Risk" value={detail.student.riskLevel === "at_risk" ? "At risk" : "On track"} />
              <MiniMetric label="Active" value={detail.student.lastActiveAt} />
            </div>

            <section>
              <h3 className="text-sm font-semibold text-white">Weakest knowledge components</h3>
              <div className="mt-3 space-y-3">
                {detail.weakKcs.map((kc) => (
                  <div key={kc.code} className="rounded-lg border border-white/10 bg-white/[0.035] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <span className="min-w-0 truncate text-sm text-slate-100">{kc.name}</span>
                      <span className="font-mono text-xs text-slate-300">{formatPercent(kc.mastery)}</span>
                    </div>
                    <Progress className="mt-3" value={kc.mastery * 100} />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold text-white">Recent activity</h3>
              <div className="mt-3 grid grid-cols-3 gap-3">
                <MiniMetric label="Submitted" value={detail.activity.submissions7d} />
                <MiniMetric label="Failed" value={detail.activity.failedAttempts7d} />
                <MiniMetric label="Hints" value={detail.activity.hintsUsed7d} />
              </div>
              <div className="mt-3 divide-y divide-white/10 rounded-lg border border-white/10 bg-white/[0.035]">
                {detail.activity.recentSubmissions.length ? detail.activity.recentSubmissions.map((submission) => (
                  <div key={submission.id} className="flex items-center justify-between gap-3 px-3 py-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm text-slate-100">{submission.exerciseTitle}</div>
                      <div className="mt-1 text-xs text-slate-500">{submission.kcCode} · {submission.createdAt}</div>
                    </div>
                    <Badge variant={statusVariant(submission.status)}>{submission.status}</Badge>
                  </div>
                )) : <div className="px-3 py-5 text-sm text-slate-400">No saved submissions yet.</div>}
              </div>
            </section>
          </div>
        ) : null}
      </section>
    </div>
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

function formatClassLabel(classId: string) {
  if (classId === "demo-python-101") {
    return "Demo Class";
  }

  return classId
    .split(/[-_]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatDashboardTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}
