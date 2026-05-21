export function formatMetricValue(value: number, aggregation?: string): string {
  if (!Number.isFinite(value)) return "—";
  if (aggregation === "count") {
    return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
  }
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: value >= 100 ? 0 : 2,
  }).format(value);
}

export function formatAggregation(aggregation: string): string {
  return aggregation === "average" ? "avg" : aggregation;
}
