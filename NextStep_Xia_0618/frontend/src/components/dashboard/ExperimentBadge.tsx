import { Shuffle, Sparkles, Waypoints } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { ExperimentGroup } from "@/types/tutor";

interface ExperimentBadgeProps {
  group: ExperimentGroup;
}

const groupMeta: Record<ExperimentGroup, { label: string; icon: typeof Sparkles; variant: "violet" | "blue" | "amber" }> = {
  adaptive: {
    label: "Adaptive",
    icon: Sparkles,
    variant: "violet"
  },
  fixed: {
    label: "Fixed",
    icon: Waypoints,
    variant: "blue"
  },
  random: {
    label: "Random",
    icon: Shuffle,
    variant: "amber"
  }
};

export function ExperimentBadge({ group }: ExperimentBadgeProps) {
  const meta = groupMeta[group];
  const Icon = meta.icon;

  return (
    <Badge variant={meta.variant}>
      <Icon className="h-3.5 w-3.5" />
      {meta.label}
    </Badge>
  );
}
