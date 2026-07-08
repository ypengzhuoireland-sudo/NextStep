import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-36 flex-col items-center justify-center rounded-lg border border-dashed border-white/12 bg-white/[0.03] px-4 py-6 text-center",
        className
      )}
    >
      <div className="grid h-10 w-10 place-items-center rounded-lg bg-white/[0.06]">
        <Icon className="h-5 w-5 text-slate-400" />
      </div>
      <div className="mt-3 text-sm font-medium text-white">{title}</div>
      <p className="mt-1 max-w-64 text-xs leading-5 text-slate-400">{description}</p>
    </div>
  );
}
