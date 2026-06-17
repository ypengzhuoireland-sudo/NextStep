import { motion } from "framer-motion";
import { BrainCircuit } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export function LoadingScreen() {
  return (
    <div className="soft-grid min-h-screen p-4 sm:p-6">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto flex max-w-[1500px] flex-col gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg border border-white/10 bg-white/[0.06]">
            <BrainCircuit className="h-5 w-5 text-cyan-200" />
          </div>
          <div>
            <Skeleton className="h-4 w-44" />
            <Skeleton className="mt-2 h-3 w-64" />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-[360px_minmax(0,1fr)_360px]">
          <Skeleton className="h-[640px]" />
          <Skeleton className="h-[640px]" />
          <Skeleton className="h-[640px]" />
        </div>
        <Skeleton className="h-64" />
      </motion.div>
    </div>
  );
}
