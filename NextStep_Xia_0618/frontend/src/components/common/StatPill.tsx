import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatPillProps {
  icon: LucideIcon;
  label: string;
  value: string;
  className?: string;
}

export function StatPill({ icon: Icon, label, value, className }: StatPillProps) {
  return (
    <div
      className={cn(
        "flex h-10 items-center gap-2 rounded-lg border border-white/10 bg-white/[0.045] px-3",
        className
      )}
    >
      <Icon className="h-4 w-4 text-slate-400" />
      <div className="leading-none">
        <div className="text-[10px] uppercase text-slate-500">{label}</div>
        <div className="mt-1 text-xs font-semibold text-slate-100">{value}</div>
      </div>
    </div>
  );
}
