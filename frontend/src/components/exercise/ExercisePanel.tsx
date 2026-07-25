import { motion } from "framer-motion";
import { BookOpen, Brain, ChevronLeft, ChevronRight, Clock3, Target } from "lucide-react";
import { LearningAdviceSection } from "@/components/mastery/LearningAdviceCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Exercise, LearningAdvice } from "@/types/tutor";
import { difficultyLabel, difficultyTone, formatPercent } from "@/utils/formatters";

interface ExercisePanelProps {
  exercise: Exercise;
  learningAdvice: LearningAdvice | null;
  isLearningAdviceLoading: boolean;
  collapsed: boolean;
  onToggleCollapsed: () => void;
}

/** Render the exercise panel interface. */
export function ExercisePanel({
  exercise,
  learningAdvice,
  isLearningAdviceLoading,
  collapsed,
  onToggleCollapsed
}: ExercisePanelProps) {
  if (collapsed) {
    return (
      <Card className="hidden min-h-[620px] items-center xl:flex xl:h-full xl:min-h-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapsed}
          aria-label="Open exercise panel"
          title="Open exercise panel"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </Card>
    );
  }

  return (
    <Card className="flex min-h-[620px] flex-col overflow-hidden xl:h-full xl:min-h-0">
      <CardHeader className="border-b border-white/10">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="blue">
              <BookOpen className="h-3.5 w-3.5" />
              Practice
            </Badge>
            <Badge className={difficultyTone(exercise.difficulty)}>{difficultyLabel(exercise.difficulty)}</Badge>
            <Badge variant="default">
              <Clock3 className="h-3.5 w-3.5" />
              {exercise.estimatedMinutes} min
            </Badge>
          </div>
          <div>
            <div className="flex items-start justify-between gap-3">
              <CardTitle className="text-xl">{exercise.title}</CardTitle>
              <Button
                className="hidden xl:inline-flex"
                variant="ghost"
                size="icon"
                onClick={onToggleCollapsed}
                aria-label="Collapse exercise panel"
                title="Collapse exercise panel"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </div>
            <CardDescription className="mt-2 text-sm">{exercise.goal}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <Tabs defaultValue="task" className="flex min-h-0 flex-1 flex-col overflow-hidden p-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="task">Task</TabsTrigger>
          <TabsTrigger value="plan">Study Plan</TabsTrigger>
        </TabsList>

        <TabsContent value="task" className="h-0 min-h-0 flex-1 overflow-y-auto overscroll-contain pr-1">
          <div className="space-y-5 pb-1">
            <section>
              <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
                <Target className="h-3.5 w-3.5" />
                Problem
              </div>
              <p className="text-sm leading-6 text-slate-200">{exercise.prompt}</p>
            </section>

            <section className="space-y-3">
              <div className="text-xs font-medium uppercase text-slate-500">Examples</div>
              {exercise.examples.map((example, index) => (
                <motion.div
                  key={`${example.input}-${index}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.04 }}
                  className="rounded-lg border border-white/10 bg-white/[0.04] p-3"
                >
                  <div className="font-mono text-xs text-cyan-100">Input: {example.input}</div>
                  <div className="mt-1 font-mono text-xs text-emerald-100">Output: {example.output}</div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{example.explanation}</p>
                </motion.div>
              ))}
            </section>

            <section>
              <div className="mb-2 text-xs font-medium uppercase text-slate-500">Constraints</div>
              <div className="space-y-2">
                {exercise.constraints.map((constraint) => (
                  <div key={constraint} className="flex gap-2 text-sm leading-5 text-slate-300">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-300/80" />
                    <span>{constraint}</span>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <div className="mb-3 flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
                <Brain className="h-3.5 w-3.5" />
                KC Tags
              </div>
              <div className="space-y-3">
                {exercise.kcTags.map((kc) => (
                  <div key={kc.code} className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">{kc.name}</div>
                        <div className="mt-1 text-xs text-slate-500">{kc.code}</div>
                      </div>
                      <div className="font-mono text-sm text-slate-200">{formatPercent(kc.mastery)}</div>
                    </div>
                    <Progress className="mt-3" value={kc.mastery * 100} />
                  </div>
                ))}
              </div>
            </section>
          </div>
        </TabsContent>

        <TabsContent value="plan" className="h-0 min-h-0 flex-1 overflow-y-auto overscroll-contain pr-1">
          <LearningAdviceSection advice={learningAdvice} isLoading={isLearningAdviceLoading} />
        </TabsContent>
      </Tabs>
    </Card>
  );
}
