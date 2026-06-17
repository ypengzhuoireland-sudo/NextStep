import { motion } from "framer-motion";
import { BookOpen, Brain, Clock3, Target } from "lucide-react";
import { LearningAdviceSection } from "@/components/mastery/LearningAdviceCard";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { Exercise, LearningAdvice } from "@/types/tutor";
import { difficultyLabel, difficultyTone, formatPercent } from "@/utils/formatters";

interface ExercisePanelProps {
  exercise: Exercise;
  learningAdvice: LearningAdvice | null;
  isLearningAdviceLoading: boolean;
}

export function ExercisePanel({ exercise, learningAdvice, isLearningAdviceLoading }: ExercisePanelProps) {
  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="border-b border-white/10">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="blue">
              <BookOpen className="h-3.5 w-3.5" />
              Practice
            </Badge>
            <Badge className={difficultyTone(exercise.difficulty)}>
              {difficultyLabel(exercise.difficulty)}
            </Badge>
            <Badge variant="default">
              <Clock3 className="h-3.5 w-3.5" />
              {exercise.estimatedMinutes} min
            </Badge>
          </div>
          <div>
            <CardTitle className="text-xl">{exercise.title}</CardTitle>
            <CardDescription className="mt-2 text-sm">{exercise.goal}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5 p-4">
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

        <LearningAdviceSection
          advice={learningAdvice}
          isLoading={isLearningAdviceLoading}
        />
      </CardContent>
    </Card>
  );
}
