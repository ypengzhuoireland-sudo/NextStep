import { motion } from "framer-motion";
import { BrainCircuit, Github, LayoutDashboard, LogOut } from "lucide-react";
import { ExperimentBadge } from "@/components/dashboard/ExperimentBadge";
import { Button } from "@/components/ui/button";
import type { PracticeSession } from "@/types/tutor";

interface SessionHeaderProps {
  session: PracticeSession;
  onOpenDashboard?: () => void;
  onLogout?: () => void;
  dashboardLabel?: string;
  learnerLabel?: string;
}

export function SessionHeader({
  session,
  onOpenDashboard,
  onLogout,
  dashboardLabel = "Dashboard",
  learnerLabel = "Python Beginner"
}: SessionHeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col gap-4 border-b border-white/10 pb-4 md:flex-row md:items-center md:justify-between"
    >
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-300/20 bg-cyan-300/10 shadow-glow">
          <BrainCircuit className="h-5 w-5 text-cyan-100" />
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-lg font-semibold text-white">NextStep AI Tutor</h1>
            <ExperimentBadge group={session.experimentGroup} />
          </div>
          <p className="mt-1 text-xs text-slate-500">{learnerLabel}</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {onOpenDashboard ? (
          <Button variant="secondary" onClick={onOpenDashboard}>
            <LayoutDashboard className="h-4 w-4" />
            {dashboardLabel}
          </Button>
        ) : null}
        <Button variant="ghost" size="icon" aria-label="Repository">
          <Github className="h-4 w-4" />
        </Button>
        {onLogout ? (
          <Button variant="ghost" onClick={onLogout}>
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        ) : null}
      </div>
    </motion.header>
  );
}
