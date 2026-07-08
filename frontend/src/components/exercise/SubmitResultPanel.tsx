import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Code2,
  Cpu,
  FileWarning,
  Gauge,
  Terminal
} from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";
import { StatPill } from "@/components/common/StatPill";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { SubmissionResult } from "@/types/tutor";

interface SubmitResultPanelProps {
  result: SubmissionResult | null;
}

export function SubmitResultPanel({ result }: SubmitResultPanelProps) {
  const passed = result?.status === "passed";

  return (
    <Card className="overflow-hidden">
      <CardHeader className="border-b border-white/10">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-cyan-200" />
            Runtime Result
          </CardTitle>
          <p className="mt-1 text-xs text-slate-500">Test cases, execution status, stdout and stderr</p>
        </div>
        {result ? (
          <Badge variant={passed ? "green" : "rose"}>
            {passed ? <CheckCircle2 className="h-3.5 w-3.5" /> : <AlertTriangle className="h-3.5 w-3.5" />}
            {passed ? "Accepted" : "Needs fix"}
          </Badge>
        ) : null}
      </CardHeader>

      <CardContent className="p-4">
        {!result ? (
          <EmptyState
            icon={Code2}
            title="No execution yet"
            description="Run or submit your code to see test cases, runtime metrics, and terminal feedback."
          />
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key={result.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              className="space-y-4"
            >
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <StatPill
                  icon={Gauge}
                  label="status"
                  value={`${result.passedCount}/${result.totalCount} passed`}
                />
                <StatPill icon={Clock3} label="runtime" value={`${result.runtimeMs} ms`} />
                <StatPill icon={Cpu} label="memory" value={`${result.memoryMb.toFixed(1)} MB`} />
                <StatPill icon={FileWarning} label="error" value={result.errorType ?? "none"} />
              </div>

              <Tabs defaultValue="cases">
                <TabsList>
                  <TabsTrigger value="cases">Test Cases</TabsTrigger>
                  <TabsTrigger value="terminal">Terminal</TabsTrigger>
                  <TabsTrigger value="mastery">Mastery Delta</TabsTrigger>
                </TabsList>

                <TabsContent value="cases">
                  <div className="grid gap-3 lg:grid-cols-2">
                    {result.testCases.map((testCase) => (
                      <div
                        key={testCase.id}
                        className="rounded-lg border border-white/10 bg-white/[0.04] p-3"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-2">
                            {testCase.passed ? (
                              <CheckCircle2 className="h-4 w-4 text-emerald-200" />
                            ) : (
                              <AlertTriangle className="h-4 w-4 text-rose-200" />
                            )}
                            <span className="text-sm font-medium text-white">{testCase.label}</span>
                          </div>
                          <Badge variant={testCase.hidden ? "violet" : testCase.passed ? "green" : "rose"}>
                            {testCase.hidden ? "Hidden" : testCase.passed ? "Passed" : "Failed"}
                          </Badge>
                        </div>
                        <div className="mt-3 grid gap-2 font-mono text-xs text-slate-300">
                          <div className="rounded-md bg-slate-950/60 p-2">input: {testCase.input}</div>
                          <div className="rounded-md bg-slate-950/60 p-2">
                            expected: {testCase.expected}
                          </div>
                          <div className="rounded-md bg-slate-950/60 p-2">actual: {testCase.actual}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="terminal">
                  <div className="terminal-surface overflow-hidden rounded-lg border border-white/10">
                    <div className="flex items-center gap-2 border-b border-white/10 px-3 py-2">
                      <span className="h-2.5 w-2.5 rounded-full bg-rose-300" />
                      <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-300" />
                      <span className="ml-2 text-xs text-slate-500">pytest-runner</span>
                    </div>
                    <pre className="max-h-52 overflow-auto p-3 font-mono text-xs leading-5 text-slate-300">
                      <code>{result.stdout}</code>
                    </pre>
                    {result.stderr ? (
                      <pre className="border-t border-rose-300/15 bg-rose-300/[0.045] p-3 font-mono text-xs leading-5 text-rose-100">
                        <code>{result.stderr}</code>
                      </pre>
                    ) : null}
                  </div>
                </TabsContent>

                <TabsContent value="mastery">
                  <div className="grid gap-3 md:grid-cols-3">
                    {result.masteryDelta.map((delta) => (
                      <div
                        key={delta.kcCode}
                        className="rounded-lg border border-white/10 bg-white/[0.04] p-3"
                      >
                        <div className="text-sm font-medium text-white">{delta.kcCode}</div>
                        <div className="mt-2 flex items-end gap-2">
                          <span className="font-mono text-2xl text-white">
                            {Math.round(delta.after * 100)}%
                          </span>
                          <span
                            className={
                              delta.after >= delta.before
                                ? "pb-1 text-xs text-emerald-200"
                                : "pb-1 text-xs text-rose-200"
                            }
                          >
                            {delta.after >= delta.before ? "+" : ""}
                            {Math.round((delta.after - delta.before) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </motion.div>
          </AnimatePresence>
        )}
      </CardContent>
    </Card>
  );
}
