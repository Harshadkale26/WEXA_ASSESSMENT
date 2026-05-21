export const CHART_COLORS = [
  "#0284c7",
  "#0ea5e9",
  "#38bdf8",
  "#6366f1",
  "#8b5cf6",
  "#a855f7",
  "#14b8a6",
  "#10b981",
  "#f59e0b",
  "#f97316",
];

export function chartColor(index: number): string {
  return CHART_COLORS[index % CHART_COLORS.length];
}
