import { AlertTriangle, BrainCircuit, CheckCircle2, ListChecks, Loader2, Target } from "lucide-react";
import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { LearningAdvice } from "@/types/tutor";

interface LearningAdviceCardProps {
  advice: LearningAdvice | null;
  isLoading: boolean;
}

export function LearningAdviceCard({ advice, isLoading }: LearningAdviceCardProps) {
  return (
    <Card>
      <LearningAdviceHeader isLoading={isLoading} className="border-b border-white/10" />

      <CardContent className="p-4">
        <LearningAdviceBody advice={advice} isLoading={isLoading} />
      </CardContent>
    </Card>
  );
}

export function LearningAdviceSection({ advice, isLoading }: LearningAdviceCardProps) {
  return (
    <section className="overflow-hidden rounded-lg border border-violet-300/15 bg-violet-300/[0.07]">
      <LearningAdviceHeader isLoading={isLoading} className="border-b border-white/10 p-3" />
      <div className="p-3">
        <LearningAdviceBody advice={advice} isLoading={isLoading} />
      </div>
    </section>
  );
}

interface LearningAdviceHeaderProps {
  isLoading: boolean;
  className?: string;
}

function LearningAdviceHeader({ isLoading, className }: LearningAdviceHeaderProps) {
  return (
    <CardHeader className={cn(className)}>
      <div>
        <CardTitle className="flex items-center gap-2">
          <BrainCircuit className="h-4 w-4 text-cyan-200" />
          AI Learning Advice
        </CardTitle>
        <p className="mt-1 text-xs text-slate-500">Overall study guidance</p>
      </div>
      <Badge variant="blue">
        {isLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <ListChecks className="h-3.5 w-3.5" />}
        Plan
      </Badge>
    </CardHeader>
  );
}

function LearningAdviceBody({ advice, isLoading }: LearningAdviceCardProps) {
  return (
    <div className="space-y-4">
      {isLoading && !advice ? (
        <p className="text-sm leading-6 text-slate-400">Generating advice from your recent practice...</p>
      ) : advice ? (
        <>
          <section>
            <div className="mb-1 text-xs font-medium uppercase text-slate-500">Summary</div>
            <p className="text-sm leading-6 text-slate-200">{advice.summary}</p>
          </section>

          <AdviceList
            icon={<CheckCircle2 className="h-4 w-4 text-emerald-200" />}
            label="Strengths"
            items={advice.strengths}
          />

          <AdviceList
            icon={<Target className="h-4 w-4 text-amber-100" />}
            label="Weaknesses"
            items={advice.weaknesses}
          />

          <AdviceList
            icon={<ListChecks className="h-4 w-4 text-cyan-200" />}
            label="Next Steps"
            items={advice.nextSteps}
            ordered
          />

          {advice.warning ? (
            <div className="flex gap-2 rounded-lg border border-amber-300/15 bg-amber-300/[0.06] p-3 text-xs leading-5 text-amber-100">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{advice.warning}</span>
            </div>
          ) : null}
        </>
      ) : (
        <div className="flex gap-2 rounded-lg border border-white/10 bg-white/[0.04] p-3 text-sm leading-6 text-slate-400">
          <AlertTriangle className="mt-1 h-4 w-4 shrink-0 text-slate-500" />
          <span>Learning advice is unavailable right now. Keep practising and try again after your next submission.</span>
        </div>
      )}
    </div>
  );
}

interface AdviceListProps {
  icon: ReactNode;
  label: string;
  items: string[];
  ordered?: boolean;
}

function AdviceList({ icon, label, items, ordered = false }: AdviceListProps) {
  if (!items.length) {
    return null;
  }

  const ListTag = ordered ? "ol" : "ul";

  return (
    <section>
      <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
        {icon}
        {label}
      </div>
      <ListTag className={ordered ? "space-y-2 pl-5 text-sm leading-6 text-slate-200" : "space-y-2 text-sm leading-6 text-slate-200"}>
        {items.map((item, index) => (
          <li key={`${label}-${index}`} className={ordered ? "list-decimal" : "flex gap-2"}>
            {ordered ? item : (
              <>
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-200/70" />
                <span>{item}</span>
              </>
            )}
          </li>
        ))}
      </ListTag>
    </section>
  );
}
