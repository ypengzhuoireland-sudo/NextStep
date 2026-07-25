import { motion } from "framer-motion";
import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { StudyAssistantDialog } from "@/components/assistant/StudyAssistantDialog";
import { LearningAnalytics } from "@/components/dashboard/LearningAnalytics";
import { SessionHeader } from "@/components/dashboard/SessionHeader";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { CodeEditor } from "@/components/exercise/CodeEditor";
import { ExercisePanel } from "@/components/exercise/ExercisePanel";
import { HintPanel } from "@/components/exercise/HintPanel";
import { NextExerciseButton } from "@/components/exercise/NextExerciseButton";
import { SubmitResultPanel } from "@/components/exercise/SubmitResultPanel";
import { LearningPath } from "@/components/mastery/LearningPath";
import { MasteryWidget } from "@/components/mastery/MasteryWidget";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { usePracticeSession } from "@/hooks/usePracticeSession";

interface PracticePageProps {
  onOpenDashboard?: () => void;
  initialExerciseId?: string;
  onLogout?: () => void;
  dashboardLabel?: string;
  learnerLabel?: string;
}

// Keep the MVP AI assistant visible without requiring a local .env flag.
const SHOW_AI_ASSISTANT = true;

/** Render the practice page interface. */
export function PracticePage({
  onOpenDashboard,
  initialExerciseId,
  onLogout,
  dashboardLabel,
  learnerLabel
}: PracticePageProps) {
  const [isExercisePanelCollapsed, setIsExercisePanelCollapsed] = useState(false);
  const [rightPanel, setRightPanel] = useState<"help" | "progress" | "path">("help");
  const {
    session,
    code,
    setCode,
    loadState,
    isRunning,
    isSubmitting,
    isHinting,
    hintingLevel,
    isRecommending,
    learningAdvice,
    isLearningAdviceLoading,
    canGoPrevious,
    weakKcs,
    handleRun,
    handleSubmit,
    handleHint,
    handleOpenExercise,
    handlePreviousExercise,
    handleNextExercise
  } = usePracticeSession(initialExerciseId);

  if (loadState === "loading" || loadState === "idle") {
    return <LoadingScreen />;
  }

  if (!session || loadState === "error") {
    return (
      <div className="soft-grid grid min-h-screen place-items-center p-6">
        <div className="glass-panel max-w-md rounded-lg p-6 text-center">
          <div className="mx-auto grid h-12 w-12 place-items-center rounded-lg bg-rose-300/10">
            <AlertTriangle className="h-6 w-6 text-rose-100" />
          </div>
          <h1 className="mt-4 text-lg font-semibold text-white">Session unavailable</h1>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            The tutor session could not be loaded. Check the API server or try again.
          </p>
          <Button className="mt-5" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <main className="soft-grid min-h-screen overflow-x-hidden p-3 sm:p-5">
      <div className="mx-auto flex max-w-[1680px] flex-col gap-4">
        <SessionHeader
          session={session}
          onOpenDashboard={onOpenDashboard}
          onLogout={onLogout}
          dashboardLabel={dashboardLabel}
          learnerLabel={learnerLabel}
        />

        <motion.section
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          className={`grid grid-cols-1 items-start gap-4 xl:items-stretch ${
            isExercisePanelCollapsed
              ? "xl:grid-cols-[64px_minmax(0,1fr)_380px]"
              : "xl:grid-cols-[360px_minmax(0,1fr)_380px]"
          }`}
        >
          <div className="min-w-0 xl:h-[min(860px,calc(100vh-11rem))] xl:min-h-0">
            <ExercisePanel
              exercise={session.exercise}
              learningAdvice={learningAdvice}
              isLearningAdviceLoading={isLearningAdviceLoading}
              collapsed={isExercisePanelCollapsed}
              onToggleCollapsed={() => setIsExercisePanelCollapsed((collapsed) => !collapsed)}
            />
          </div>

          <div className="min-w-0 xl:h-[min(860px,calc(100vh-11rem))] xl:min-h-0">
            <CodeEditor
              code={code}
              starterCode={session.exercise.starterCode}
              latestResult={session.latestResult}
              isRunning={isRunning}
              isSubmitting={isSubmitting}
              onCodeChange={setCode}
              onRun={handleRun}
              onSubmit={handleSubmit}
            />
          </div>

          <aside className="flex min-h-0 min-w-0 flex-col gap-4 xl:h-[min(860px,calc(100vh-11rem))]">
            <Tabs
              value={rightPanel}
              onValueChange={(value) => setRightPanel(value as "help" | "progress" | "path")}
              className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-white/10 bg-slate-950/45 p-3"
            >
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="help">Help</TabsTrigger>
                <TabsTrigger value="progress">Progress</TabsTrigger>
                <TabsTrigger value="path">Path</TabsTrigger>
              </TabsList>
              <TabsContent value="help" className="h-0 min-h-0 flex-1 overflow-y-auto overscroll-contain pr-1">
                <HintPanel
                  messages={session.hintMessages}
                  isHinting={isHinting}
                  hintingLevel={hintingLevel}
                  onRequestHint={handleHint}
                />
              </TabsContent>
              <TabsContent value="progress" className="h-0 min-h-0 flex-1 overflow-y-auto overscroll-contain pr-1">
                <MasteryWidget
                  masteryProfile={session.masteryProfile}
                  targetKcs={session.exercise.kcTags}
                  weakKcs={weakKcs}
                />
              </TabsContent>
              <TabsContent value="path" className="h-0 min-h-0 flex-1 overflow-y-auto overscroll-contain pr-1">
                <div className="space-y-3">
                  <NextExerciseButton
                    exercise={session.exercise}
                    isLoading={isRecommending}
                    disabled={isRunning || isSubmitting || isHinting}
                    canGoPrevious={canGoPrevious}
                    onPreviousExercise={handlePreviousExercise}
                    onNextExercise={handleNextExercise}
                  />
                  <LearningPath items={session.learningPath} />
                </div>
              </TabsContent>
            </Tabs>
          </aside>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08, duration: 0.45, ease: "easeOut" }}
          className="grid gap-4 2xl:grid-cols-[1fr_0.95fr]"
        >
          <SubmitResultPanel result={session.latestResult} />
          <LearningAnalytics data={session.dashboardSeries} />
        </motion.section>
      </div>
      {SHOW_AI_ASSISTANT ? (
        <StudyAssistantDialog
          currentExerciseId={session.exercise.id}
          disabled={isRunning || isSubmitting || isHinting || isRecommending}
          onStartExercise={handleOpenExercise}
        />
      ) : null}
    </main>
  );
}
