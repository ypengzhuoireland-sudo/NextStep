import { cn } from "@/lib/utils";

/** Render the skeleton interface. */
function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-lg bg-white/[0.07]", className)}
      {...props}
    />
  );
}

export { Skeleton };
