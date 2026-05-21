"use client";

import { formatAggregation, formatMetricValue } from "@/lib/format";
import type { WidgetDataResponse } from "@/types/dashboard";

export function KpiChart({ data }: { data: WidgetDataResponse }) {
  const value = data.value ?? 0;
  return (
    <div className="flex h-full min-h-[120px] flex-col justify-center px-2">
      <p className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
        {formatMetricValue(value, data.aggregation)}
      </p>
      <p className="mt-2 text-sm text-muted">
        {formatAggregation(data.aggregation)} · {data.metric}
      </p>
    </div>
  );
}
