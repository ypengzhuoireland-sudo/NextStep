import { CheckCircle2, CircleDot, Lock, Route } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LearningPathItem } from "@/types/tutor";
import { difficultyLabel, difficultyTone } from "@/utils/formatters";

interface LearningPathProps {
  items: LearningPathItem[];
}

export function LearningPath({ items }: LearningPathProps) {
  return (
    <Card>
      <CardHeader className="border-b border-white/10">
        <CardTitle className="flex items-center gap-2">
          <Route className="h-4 w-4 text-cyan-200" />
          Learning Path
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="space-y-3">
          {items.map((item, index) => {
            const Icon = item.state === "done" ? CheckCircle2 : item.state === "locked" ? Lock : CircleDot;
            return (
              <div key={item.id} className="relative flex gap-3">
                {index !== items.length - 1 ? (
                  <div className="absolute left-4 top-9 h-[calc(100%-1.5rem)] w-px bg-white/10" />
                ) : null}
                <div
                  className={`z-10 grid h-8 w-8 shrink-0 place-items-center rounded-lg border ${
                    item.state === "current"
                      ? "border-cyan-300/30 bg-cyan-300/12 text-cyan-100"
                      : item.state === "locked"
                        ? "border-white/10 bg-white/[0.04] text-slate-500"
                        : "border-emerald-300/25 bg-emerald-300/10 text-emerald-100"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1 rounded-lg border border-white/10 bg-white/[0.035] p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-white">{item.title}</div>
                      <div className="mt-1 text-xs text-slate-500">{item.kcCode}</div>
                    </div>
                    <Badge className={difficultyTone(item.difficulty)}>
                      {difficultyLabel(item.difficulty)}
                    </Badge>
                  </div>
                  <div className="mt-2 text-xs text-slate-500">{item.etaMinutes} min</div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
