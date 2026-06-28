import Editor from "@monaco-editor/react";
import type { ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  Braces,
  CheckCircle2,
  Loader2,
  Play,
  RotateCcw,
  Send,
  Settings2,
  Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { SubmissionResult } from "@/types/tutor";

interface CodeEditorProps {
  code: string;
  starterCode: string;
  latestResult: SubmissionResult | null;
  isRunning: boolean;
  isSubmitting: boolean;
  onCodeChange: (code: string) => void;
  onRun: () => void;
  onSubmit: () => void;
}

export function CodeEditor({
  code,
  starterCode,
  latestResult,
  isRunning,
  isSubmitting,
  onCodeChange,
  onRun,
  onSubmit
}: CodeEditorProps) {
  const busy = isRunning || isSubmitting;

  return (
    <div className="glass-panel flex min-h-[620px] flex-col overflow-hidden rounded-lg">
      <div className="flex min-h-14 flex-wrap items-center justify-between gap-3 border-b border-white/10 px-3 py-2">
        <div className="flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 bg-white/[0.06]">
            <Braces className="h-4 w-4 text-cyan-200" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white">Python Workspace</div>
            <div className="text-xs text-slate-500">main.py · Python 3.11</div>
          </div>
        </div>

        <TooltipProvider delayDuration={180}>
          <div className="flex items-center gap-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onCodeChange(starterCode)}
                  disabled={busy}
                  aria-label="Reset code"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Reset code</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Editor settings">
                  <Settings2 className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Editor settings</TooltipContent>
            </Tooltip>

            <Button variant="terminal" onClick={onRun} disabled={busy}>
              {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              Run Code
            </Button>
            <Button onClick={onSubmit} disabled={busy}>
              {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              Submit
            </Button>
          </div>
        </TooltipProvider>
      </div>

      <div className="relative h-[520px] flex-1">
        <Editor
          height="520px"
          defaultLanguage="python"
          value={code}
          theme="vs-dark"
          loading={<EditorLoading />}
          onChange={(value) => onCodeChange(value ?? "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: "JetBrains Mono, Consolas, monospace",
            fontLigatures: true,
            lineNumbersMinChars: 3,
            padding: { top: 18, bottom: 18 },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            cursorBlinking: "smooth",
            roundedSelection: true,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: "on"
          }}
        />

        <AnimatePresence>
          {busy ? (
            <EditorStatusOverlay key="busy" tone="neutral">
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <Sparkles className="h-3.5 w-3.5 text-cyan-200" />
                {isSubmitting ? "Evaluating tests and updating mastery" : "Running public tests"}
              </div>
              <div className="flex items-center gap-1 text-xs text-emerald-100">
                <CheckCircle2 className="h-3.5 w-3.5" />
                sandbox ready
              </div>
            </EditorStatusOverlay>
          ) : latestResult ? (
            <EditorStatusOverlay
              key={latestResult.id}
              tone={latestResult.status === "passed" ? "success" : "error"}
            >
              <div className="flex min-w-0 items-center gap-2 text-xs text-slate-200">
                {latestResult.status === "passed" ? (
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-200" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-200" />
                )}
                <span className="font-medium text-white">Last result</span>
                <span className="text-slate-400">
                  {latestResult.passedCount}/{latestResult.totalCount} tests
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-300">
                <span>{latestResult.runtimeMs} ms</span>
                <span className={masteryDeltaTone(latestResult)}>
                  {formatMasteryDelta(latestResult)}
                </span>
              </div>
            </EditorStatusOverlay>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}

function EditorStatusOverlay({
  tone,
  children
}: {
  tone: "neutral" | "success" | "error";
  children: ReactNode;
}) {
  const toneClass =
    tone === "success"
      ? "border-emerald-300/25 bg-emerald-950/55"
      : tone === "error"
        ? "border-rose-300/25 bg-rose-950/55"
        : "border-white/10 bg-slate-950/82";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 8 }}
      className={cn(
        "pointer-events-none absolute inset-x-3 bottom-3 flex items-center justify-between gap-3 rounded-lg border px-3 py-2 shadow-panel backdrop-blur",
        toneClass
      )}
    >
      {children}
    </motion.div>
  );
}

function formatMasteryDelta(result: SubmissionResult) {
  if (!result.masteryDelta.length) {
    return "mastery unchanged";
  }

  const totalDelta = result.masteryDelta.reduce(
    (total, delta) => total + delta.after - delta.before,
    0
  );
  const averageDelta = totalDelta / result.masteryDelta.length;
  const rounded = Math.round(averageDelta * 100);

  if (rounded === 0) {
    return "mastery unchanged";
  }

  return `${rounded > 0 ? "+" : ""}${rounded}% mastery`;
}

function masteryDeltaTone(result: SubmissionResult) {
  const text = formatMasteryDelta(result);

  if (text.startsWith("+")) {
    return "text-emerald-100";
  }

  if (text.startsWith("-")) {
    return "text-rose-100";
  }

  return "text-slate-400";
}

function EditorLoading() {
  return (
    <div className="flex h-full items-center justify-center bg-slate-950">
      <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.05] px-3 py-2 text-sm text-slate-300">
        <Loader2 className={cn("h-4 w-4 animate-spin text-cyan-200")} />
        Loading editor
      </div>
    </div>
  );
}
