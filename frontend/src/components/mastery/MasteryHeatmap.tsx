import { motion } from "framer-motion";
import type { KnowledgeComponent } from "@/types/tutor";
import { formatPercent, heatmapColor } from "@/utils/formatters";

interface MasteryHeatmapProps {
  items: KnowledgeComponent[];
}

export function MasteryHeatmap({ items }: MasteryHeatmapProps) {
  return (
    <div className="grid grid-cols-5 gap-2">
      {items.map((kc, index) => (
        <motion.div
          key={kc.code}
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.025 }}
          title={`${kc.name}: ${formatPercent(kc.mastery)}`}
          className="group relative aspect-square min-h-0 rounded-lg border border-white/10 bg-white/[0.04] p-1 transition-transform hover:-translate-y-0.5"
        >
          <div className={`h-full w-full rounded-md ${heatmapColor(kc.mastery)}`} />
          <div className="pointer-events-none absolute inset-x-1 bottom-1 truncate rounded bg-slate-950/70 px-1 py-0.5 text-center text-[9px] text-white opacity-0 transition-opacity group-hover:opacity-100">
            {kc.code}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
