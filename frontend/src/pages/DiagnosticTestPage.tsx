import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  BrainCircuit,
  Check,
  CheckCircle2,
  Clock3,
  Loader2,
  Target,
  TriangleAlert
} from "lucide-react";
import {
  getDiagnosticQuestions,
  submitDiagnosticAnswers,
  type DiagnosticQuestionResponse,
  type DiagnosticResult
} from "@/api/diagnostic";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface DiagnosticTestPageProps {
  onComplete: (exerciseId?: string) => void;
}

type PageState = "loading" | "ready" | "submitting" | "result" | "error";

export function DiagnosticTestPage({ onComplete }: DiagnosticTestPageProps) {
  const [assessment, setAssessment] = useState<DiagnosticQuestionResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [result, setResult] = useState<DiagnosticResult | null>(null);
  const [state, setState] = useState<PageState>("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    getDiagnosticQuestions()
      .then((data) => {
        if (!mounted) return;
        setAssessment(data);
        setState("ready");
      })
      .catch((reason) => {
        if (!mounted) return;
        setError(reason instanceof Error ? reason.message : "Unable to load the diagnostic test");
        setState("error");
      });
    return () => {
      mounted = false;
    };
  }, []);

  const answeredCount = Object.keys(answers).length;
  const question = assessment?.questions[currentIndex];
  const isLastQuestion = currentIndex === (assessment?.questions.length ?? 0) - 1;
  const allAnswered = answeredCount === assessment?.totalQuestions;

  const groupedResults = useMemo(() => {
    if (!result) return { strengths: [], developing: [], weaknesses: [] };
    return {
      strengths: result.kcResults.filter((item) => item.level === "strength"),
      developing: result.kcResults.filter((item) => item.level === "developing"),
      weaknesses: result.kcResults.filter((item) => item.level === "weakness")
    };
  }, [result]);

  async function submit() {
    if (!assessment || !allAnswered) return;
    setState("submitting");
    setError("");
    try {
      const response = await submitDiagnosticAnswers(answers);
      setResult(response);
      setState("result");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to score the diagnostic test");
      setState("ready");
    }
  }

  if (state === "loading") {
    return (
      <main className="soft-grid grid min-h-screen place-items-center p-6">
        <Loader2 className="h-7 w-7 animate-spin text-cyan-200" aria-label="Loading diagnostic test" />
      </main>
    );
  }

  if (state === "error" || !assessment || !question) {
    return (
      <main className="soft-grid grid min-h-screen place-items-center p-6">
        <section className="glass-panel max-w-md rounded-lg p-6 text-center">
          <TriangleAlert className="mx-auto h-7 w-7 text-rose-200" />
          <h1 className="mt-4 text-lg font-semibold">Diagnostic unavailable</h1>
          <p className="mt-2 text-sm text-slate-400">{error}</p>
          <Button className="mt-5" onClick={() => window.location.reload()}>Retry</Button>
        </section>
      </main>
    );
  }

  if (state === "result" && result) {
    return (
      <DiagnosticResults
        result={result}
        strengths={groupedResults.strengths}
        developing={groupedResults.developing}
        weaknesses={groupedResults.weaknesses}
        onStart={onComplete}
      />
    );
  }

  return (
    <main className="soft-grid min-h-screen p-3 sm:p-6">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-300/20 bg-cyan-300/10">
              <BrainCircuit className="h-5 w-5 text-cyan-100" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">Python Foundation Diagnostic</h1>
              <p className="mt-1 text-xs text-slate-500">12 knowledge components | 24 questions</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Clock3 className="h-4 w-4" />
            About {assessment.estimatedMinutes} minutes
          </div>
        </header>

        <section className="mt-5 grid gap-5 lg:grid-cols-[220px_minmax(0,1fr)]">
          <aside className="border-b border-white/10 pb-5 lg:border-b-0 lg:border-r lg:pb-0 lg:pr-5">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Progress</span>
              <span>{answeredCount}/{assessment.totalQuestions}</span>
            </div>
            <Progress className="mt-3" value={(answeredCount / assessment.totalQuestions) * 100} />
            <div className="mt-5 grid grid-cols-8 gap-1.5 lg:grid-cols-4">
              {assessment.questions.map((item, index) => (
                <button
                  key={item.id}
                  type="button"
                  aria-label={`Question ${index + 1}`}
                  onClick={() => setCurrentIndex(index)}
                  className={cn(
                    "grid aspect-square place-items-center rounded-md border text-xs transition-colors",
                    index === currentIndex
                      ? "border-cyan-300/50 bg-cyan-300/15 text-cyan-100"
                      : answers[item.id]
                        ? "border-emerald-300/30 bg-emerald-300/10 text-emerald-100"
                        : "border-white/10 bg-white/[0.035] text-slate-500 hover:bg-white/[0.07]"
                  )}
                >
                  {answers[item.id] ? <Check className="h-3.5 w-3.5" /> : index + 1}
                </button>
              ))}
            </div>
          </aside>

          <motion.section
            key={question.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="min-w-0"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Badge variant="blue">{question.kcName}</Badge>
              <span className="text-xs text-slate-500">Question {currentIndex + 1} of {assessment.totalQuestions}</span>
            </div>
            <h2 className="mt-5 text-xl font-semibold leading-8 text-white">{question.prompt}</h2>

            {question.code ? (
              <pre className="terminal-surface mt-4 overflow-x-auto rounded-lg border border-white/10 p-4 font-mono text-sm leading-6 text-slate-200">
                <code>{question.code}</code>
              </pre>
            ) : null}

            <div className="mt-5 grid gap-2.5">
              {question.options.map((option) => {
                const selected = answers[question.id] === option.id;
                return (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setAnswers((current) => ({ ...current, [question.id]: option.id }))}
                    className={cn(
                      "flex min-h-12 w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors",
                      selected
                        ? "border-cyan-300/45 bg-cyan-300/10 text-white"
                        : "border-white/10 bg-white/[0.035] text-slate-300 hover:bg-white/[0.07]"
                    )}
                  >
                    <span className={cn(
                      "grid h-7 w-7 shrink-0 place-items-center rounded-md border font-mono text-xs",
                      selected ? "border-cyan-300/50 bg-cyan-300/15 text-cyan-100" : "border-white/10 text-slate-500"
                    )}>
                      {selected ? <Check className="h-4 w-4" /> : option.id}
                    </span>
                    <span className="min-w-0 break-words">{option.text}</span>
                  </button>
                );
              })}
            </div>

            {error ? <p className="mt-4 text-sm text-rose-200">{error}</p> : null}

            <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-4">
              <Button
                variant="secondary"
                disabled={currentIndex === 0 || state === "submitting"}
                onClick={() => setCurrentIndex((index) => index - 1)}
              >
                <ArrowLeft className="h-4 w-4" /> Previous
              </Button>

              {isLastQuestion ? (
                <Button disabled={!allAnswered || state === "submitting"} onClick={submit}>
                  {state === "submitting" ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  Submit test
                </Button>
              ) : (
                <Button
                  disabled={!answers[question.id]}
                  onClick={() => setCurrentIndex((index) => index + 1)}
                >
                  Next <ArrowRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </motion.section>
        </section>
      </div>
    </main>
  );
}

interface ResultSectionProps {
  result: DiagnosticResult;
  strengths: DiagnosticResult["kcResults"];
  developing: DiagnosticResult["kcResults"];
  weaknesses: DiagnosticResult["kcResults"];
  onStart: (exerciseId?: string) => void;
}

function DiagnosticResults({ result, strengths, developing, weaknesses, onStart }: ResultSectionProps) {
  return (
    <main className="soft-grid min-h-screen p-3 sm:p-6">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-cyan-100">
              <CheckCircle2 className="h-5 w-5" />
              <span className="text-sm font-medium">Diagnostic complete</span>
            </div>
            <h1 className="mt-3 text-2xl font-semibold">Your Python foundation profile</h1>
          </div>
          <div className="text-left sm:text-right">
            <div className="text-3xl font-semibold text-white">{Math.round(result.overallScore * 100)}%</div>
            <div className="mt-1 text-xs text-slate-500">{result.correctAnswers} of {result.totalQuestions} correct</div>
          </div>
        </header>

        <section className="mt-5 grid gap-4 md:grid-cols-3">
          <ResultGroup title="Strengths" items={strengths} tone="green" empty="No confirmed strengths yet" />
          <ResultGroup title="Developing" items={developing} tone="amber" empty="No developing areas" />
          <ResultGroup title="Focus areas" items={weaknesses} tone="rose" empty="No major gaps identified" />
        </section>

        <section className="mt-6 border-t border-white/10 pt-5">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-cyan-200" />
            <h2 className="text-base font-semibold">Recommended starting exercises</h2>
          </div>
          <div className="mt-3 divide-y divide-white/10 border-y border-white/10">
            {result.recommendations.map((item, index) => (
              <div key={item.exerciseId} className="grid gap-3 py-4 md:grid-cols-[40px_minmax(0,1fr)_auto] md:items-center">
                <div className="grid h-8 w-8 place-items-center rounded-md bg-white/[0.06] font-mono text-xs text-slate-300">{index + 1}</div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-sm font-medium text-white">{item.exerciseTitle}</h3>
                    <Badge>{item.kcName}</Badge>
                    <Badge variant="blue">{item.difficulty}</Badge>
                  </div>
                  <p className="mt-1.5 text-xs leading-5 text-slate-400">{item.reason}</p>
                </div>
                <Button variant={index === 0 ? "default" : "secondary"} onClick={() => onStart(item.exerciseId)}>
                  Start <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {result.kcResults.map((item) => (
            <div key={item.kcId} className="min-w-0 border-l border-white/10 px-3 py-2">
              <div className="truncate text-xs text-slate-400" title={item.kcName}>{item.kcName}</div>
              <div className="mt-2 font-mono text-lg text-white">{Math.round(item.mastery * 100)}%</div>
              <div className="mt-1 text-[11px] text-slate-600">{item.correct}/{item.total} correct</div>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}

function ResultGroup({
  title,
  items,
  tone,
  empty
}: {
  title: string;
  items: DiagnosticResult["kcResults"];
  tone: "green" | "amber" | "rose";
  empty: string;
}) {
  return (
    <section className="border-l border-white/10 px-4 py-2">
      <Badge variant={tone}>{title}</Badge>
      <div className="mt-3 space-y-2">
        {items.length ? items.map((item) => (
          <div key={item.kcId} className="flex items-center justify-between gap-3 text-sm">
            <span className="min-w-0 truncate text-slate-300" title={item.kcName}>{item.kcName}</span>
            <span className="font-mono text-xs text-slate-500">{Math.round(item.mastery * 100)}%</span>
          </div>
        )) : <p className="text-sm text-slate-600">{empty}</p>}
      </div>
    </section>
  );
}
