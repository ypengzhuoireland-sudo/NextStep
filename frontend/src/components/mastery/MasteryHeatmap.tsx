import { motion } from "framer-motion";
import type { KnowledgeComponent } from "@/types/tutor";
import { formatPercent, heatmapStyle } from "@/utils/formatters";

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
          title={`${kc.code} · ${kc.name}: ${formatPercent(kc.mastery)}`}
          aria-label={`${kc.name} ${formatPercent(kc.mastery)} mastery`}
          className="group relative aspect-square min-h-0 rounded-lg border border-white/10 bg-white/[0.04] p-1 transition-transform hover:-translate-y-0.5"
        >
          <div
            className="flex h-full w-full flex-col justify-between rounded-md p-2 text-white"
            style={heatmapStyle(kc.mastery)}
          >
            <span className="text-center text-[11px] font-semibold leading-none text-white/90">
              {kc.shortName ?? kc.name ?? kc.code}
            </span>
            <span className="text-right font-mono text-xs font-semibold leading-none drop-shadow">
              {formatPercent(kc.mastery)}
            </span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
