"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { chartColor } from "@/components/dashboard/chart-colors";
import { ChartTooltipContent } from "@/components/dashboard/charts/chart-tooltip";
import type { WidgetDataResponse } from "@/types/dashboard";

function toChartData(data: WidgetDataResponse) {
  return data.points.map((p) => ({
    label: p.label,
    value: p.value,
  }));
}

export function LineChartWidget({ data }: { data: WidgetDataResponse }) {
  const chartData = toChartData(data);

  if (!chartData.length) {
    return <p className="py-8 text-center text-sm text-muted">No data for this period</p>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%" minHeight={200}>
      <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border))" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 11, fill: "rgb(var(--muted))" }}
          tickLine={false}
          axisLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fontSize: 11, fill: "rgb(var(--muted))" }}
          tickLine={false}
          axisLine={false}
          width={48}
          tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v))}
        />
        <Tooltip content={<ChartTooltipContent />} />
        <Line
          type="monotone"
          dataKey="value"
          name={data.metric}
          stroke={chartColor(0)}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
