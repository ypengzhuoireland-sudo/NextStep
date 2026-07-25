import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Handle cn. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
