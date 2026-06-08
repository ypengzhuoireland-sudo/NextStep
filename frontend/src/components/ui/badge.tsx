import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-white/10 bg-white/[0.06] text-slate-200",
        blue: "border-sky-300/25 bg-sky-300/10 text-sky-100",
        violet: "border-violet-300/25 bg-violet-300/10 text-violet-100",
        green: "border-emerald-300/25 bg-emerald-300/10 text-emerald-100",
        amber: "border-amber-300/25 bg-amber-300/10 text-amber-100",
        rose: "border-rose-300/25 bg-rose-300/10 text-rose-100"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
