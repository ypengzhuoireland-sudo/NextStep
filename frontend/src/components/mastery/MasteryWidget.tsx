import { ArrowDownRight, ArrowUpRight, BrainCircuit } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { MasteryHeatmap } from "@/components/mastery/MasteryHeatmap";
import { MasteryRing } from "@/components/mastery/MasteryRing";
import { cn } from "@/lib/utils";
import type { KnowledgeComponent } from "@/types/tutor";
import { formatPercent, masteryColor, masteryStateLabel } from "@/utils/formatters";

interface MasteryWidgetProps {
  masteryProfile: KnowledgeComponent[];
  targetKcs: KnowledgeComponent[];
  weakKcs: KnowledgeComponent[];
}

export function MasteryWidget({ masteryProfile, targetKcs, weakKcs }: MasteryWidgetProps) {
  const average =
    masteryProfile.reduce((total, kc) => total + kc.mastery, 0) / Math.max(masteryProfile.length, 1);

  return (
    <Card>
      <CardHeader className="border-b border-white/10">
        <div>
          <CardTitle className="flex items-center gap-2">
            <BrainCircuit className="h-4 w-4 text-cyan-200" />
            Mastery
          </CardTitle>
          <p className="mt-1 text-xs text-slate-500">Per-KC learning state</p>
        </div>
        <Badge variant={average >= 0.7 ? "green" : "amber"}>{formatPercent(average)}</Badge>
      </CardHeader>

      <CardContent className="space-y-5 p-4">
        <div className="space-y-2">
          <div className="text-xs font-medium uppercase text-slate-500">Current Exercise KC</div>
          {targetKcs.map((kc) => (
            <div
              key={kc.code}
              className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.06] p-3"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-white">{kc.name}</div>
                  <div className="mt-1 text-xs text-slate-500">{kc.code}</div>
                </div>
                <div className="text-right">
                  <div className={`font-mono text-sm ${masteryColor(kc.mastery)}`}>
                    {formatPercent(kc.mastery)}
                  </div>
                  <div className={cn("mt-1 font-mono text-xs", trendTone(kc.trend))}>
                    {formatTrend(kc.trend)}
                  </div>
                </div>
              </div>
              <Progress className="mt-3" value={kc.mastery * 100} />
            </div>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <MasteryRing value={average} label="overall" />
          <div className="min-w-0 flex-1 space-y-3">
            {weakKcs.slice(0, 3).map((kc) => (
              <div key={kc.code}>
                <div className="mb-1 flex items-center justify-between gap-3">
                  <span className="truncate text-xs font-medium text-slate-300">{kc.name}</span>
                  <span className={`font-mono text-xs ${masteryColor(kc.mastery)}`}>
                    {formatPercent(kc.mastery)}
                  </span>
                </div>
                <Progress value={kc.mastery * 100} />
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 text-xs font-medium uppercase text-slate-500">KC Heatmap</div>
          <MasteryHeatmap items={masteryProfile} />
        </div>

        <div className="space-y-2">
          <div className="text-xs font-medium uppercase text-slate-500">Weak KC</div>
          {weakKcs.map((kc) => {
            const TrendIcon = kc.trend >= 0 ? ArrowUpRight : ArrowDownRight;
            return (
              <div
                key={kc.code}
                className="flex items-center justify-between gap-3 rounded-lg border border-white/10 bg-white/[0.04] p-2.5"
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-white">{kc.name}</div>
                  <div className="mt-1 text-xs text-slate-500">{masteryStateLabel(kc.state)}</div>
                </div>
                <div className="flex items-center gap-2">
                  <TrendIcon
                    className={kc.trend >= 0 ? "h-4 w-4 text-emerald-200" : "h-4 w-4 text-rose-200"}
                  />
                  <span className="font-mono text-xs text-slate-300">
                    {formatTrend(kc.trend)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function formatTrend(trend: number) {
  const rounded = Math.round(trend * 100);
  return `${rounded >= 0 ? "+" : ""}${rounded}%`;
}

function trendTone(trend: number) {
  if (trend > 0) {
    return "text-emerald-100";
  }

  if (trend < 0) {
    return "text-rose-100";
  }

  return "text-slate-400";
}
