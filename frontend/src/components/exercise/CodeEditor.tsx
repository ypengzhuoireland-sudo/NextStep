import Editor from "@monaco-editor/react";
import { AnimatePresence, motion } from "framer-motion";
import {
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

interface CodeEditorProps {
  code: string;
  starterCode: string;
  isRunning: boolean;
  isSubmitting: boolean;
  onCodeChange: (code: string) => void;
  onRun: () => void;
  onSubmit: () => void;
}

export function CodeEditor({
  code,
  starterCode,
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
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="pointer-events-none absolute inset-x-3 bottom-3 flex items-center justify-between rounded-lg border border-white/10 bg-slate-950/82 px-3 py-2 shadow-panel backdrop-blur"
            >
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <Sparkles className="h-3.5 w-3.5 text-cyan-200" />
                {isSubmitting ? "Evaluating tests and updating mastery" : "Running public tests"}
              </div>
              <div className="flex items-center gap-1 text-xs text-emerald-100">
                <CheckCircle2 className="h-3.5 w-3.5" />
                sandbox ready
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
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
