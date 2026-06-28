import {
  GitBranch,
  Loader2,
  MoveLeft,
  MoveRight,
  Sparkles
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Exercise } from "@/types/tutor";

interface NextExerciseButtonProps {
  exercise: Exercise;
  isLoading: boolean;
  disabled?: boolean;
  canGoPrevious: boolean;
  onPreviousExercise: () => void;
  onNextExercise: () => void;
}

export function NextExerciseButton({
  exercise,
  isLoading,
  disabled = false,
  canGoPrevious,
  onPreviousExercise,
  onNextExercise
}: NextExerciseButtonProps) {
  return (
    <Card>
      <CardHeader className="border-b border-white/10">
        <CardTitle className="flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-cyan-200" />
          Next Exercise
        </CardTitle>
        <Badge variant="violet">
          <Sparkles className="h-3.5 w-3.5" />
          {Math.round(exercise.recommendation.confidence * 100)}%
        </Badge>
      </CardHeader>

      <CardContent className="space-y-3 p-4">
        <p className="text-sm leading-6 text-slate-200">{exercise.recommendation.reason}</p>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between xl:flex-col xl:items-stretch">
          <span className="min-w-0 truncate text-xs text-slate-500">
            {exercise.recommendation.strategy}
          </span>
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="secondary"
              onClick={onPreviousExercise}
              disabled={disabled || isLoading || !canGoPrevious}
            >
              <MoveLeft className="h-4 w-4" />
              Previous
            </Button>
            <Button onClick={onNextExercise} disabled={disabled || isLoading}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <MoveRight className="h-4 w-4" />
              )}
              Get Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
