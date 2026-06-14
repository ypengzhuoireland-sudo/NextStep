import type { Difficulty, MasteryState } from "@/types/tutor";
import type { CSSProperties } from "react";

export function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function difficultyLabel(difficulty: Difficulty) {
  const labels: Record<Difficulty, string> = {
    easy: "Easy",
    medium: "Medium",
    hard: "Hard"
  };

  return labels[difficulty];
}

export function difficultyTone(difficulty: Difficulty) {
  const tones: Record<Difficulty, string> = {
    easy: "border-emerald-400/25 bg-emerald-400/10 text-emerald-200",
    medium: "border-amber-300/25 bg-amber-300/10 text-amber-100",
    hard: "border-rose-300/25 bg-rose-300/10 text-rose-100"
  };

  return tones[difficulty];
}

export function masteryStateLabel(state: MasteryState) {
  const labels: Record<MasteryState, string> = {
    needs_practice: "Needs practice",
    almost_there: "Almost there",
    mastered: "Mastered"
  };

  return labels[state];
}

export function masteryColor(value: number) {
  if (value >= 0.75) {
    return "text-emerald-200";
  }

  if (value >= 0.6) {
    return "text-cyan-200";
  }

  if (value >= 0.45) {
    return "text-amber-100";
  }

  return "text-rose-100";
}

export function heatmapColor(value: number) {
  if (value >= 0.8) {
    return "bg-emerald-300/80 shadow-[0_0_18px_rgba(110,231,183,0.28)]";
  }

  if (value >= 0.65) {
    return "bg-cyan-300/70 shadow-[0_0_18px_rgba(103,232,249,0.22)]";
  }

  if (value >= 0.5) {
    return "bg-amber-300/70 shadow-[0_0_18px_rgba(252,211,77,0.18)]";
  }

  return "bg-rose-300/70 shadow-[0_0_18px_rgba(253,164,175,0.18)]";
}

export function heatmapStyle(value: number): CSSProperties {
  const clamped = clampProbability(value);
  const hue =
    clamped < 0.5
      ? (345 + 57 * (clamped / 0.5)) % 360
      : 42 + 116 * ((clamped - 0.5) / 0.5);
  const saturation = 70;
  const lightness = 42 + clamped * 16;
  const alpha = 0.46 + clamped * 0.34;

  return {
    background: `linear-gradient(135deg, hsl(${hue} ${saturation}% ${lightness}% / ${alpha}), hsl(${hue} ${saturation}% ${Math.max(lightness - 8, 34)}% / ${Math.min(alpha + 0.1, 0.9)}))`,
    boxShadow: `0 0 ${10 + clamped * 16}px hsl(${hue} ${saturation}% ${lightness}% / ${0.12 + clamped * 0.22})`
  };
}

function clampProbability(value: number) {
  return Math.max(0, Math.min(1, value));
}
