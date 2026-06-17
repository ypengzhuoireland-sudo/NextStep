import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const heatmapPath = path.join(root, "src", "components", "mastery", "MasteryHeatmap.tsx");
const formatterPath = path.join(root, "src", "utils", "formatters.ts");

const heatmapSource = fs.readFileSync(heatmapPath, "utf8");
const formatterSource = fs.readFileSync(formatterPath, "utf8");

const checks = [
  {
    ok: formatterSource.includes("export function heatmapStyle"),
    message: "formatters.ts should export heatmapStyle for continuous heatmap coloring."
  },
  {
    ok: formatterSource.includes("clampProbability"),
    message: "heatmapStyle should clamp mastery values before deriving visual intensity."
  },
  {
    ok: heatmapSource.includes("style={heatmapStyle(kc.mastery)}"),
    message: "MasteryHeatmap should use heatmapStyle(kc.mastery) instead of coarse color classes."
  },
  {
    ok: heatmapSource.includes("{formatPercent(kc.mastery)}"),
    message: "MasteryHeatmap should show the mastery percentage inside each tile."
  },
  {
    ok: heatmapSource.includes("aria-label={`${kc.name} ${formatPercent(kc.mastery)} mastery`}"),
    message: "MasteryHeatmap tiles should expose the KC name and percent to assistive technology."
  }
];

const failures = checks.filter((check) => !check.ok);

if (failures.length) {
  console.error(failures.map((failure) => `- ${failure.message}`).join("\n"));
  process.exit(1);
}

console.log("Heatmap uses a continuous mastery scale with visible percentages.");
