"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
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

export function BarChartWidget({ data }: { data: WidgetDataResponse }) {
  const chartData = toChartData(data);

  if (!chartData.length) {
    return <p className="py-8 text-center text-sm text-muted">No data for this period</p>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%" minHeight={200}>
      <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border))" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 11, fill: "rgb(var(--muted))" }}
          tickLine={false}
          axisLine={false}
          interval={0}
          angle={chartData.length > 6 ? -35 : 0}
          textAnchor={chartData.length > 6 ? "end" : "middle"}
          height={chartData.length > 6 ? 56 : 30}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "rgb(var(--muted))" }}
          tickLine={false}
          axisLine={false}
          width={48}
        />
        <Tooltip content={<ChartTooltipContent />} cursor={{ fill: "rgb(var(--muted-bg) / 0.5)" }} />
        <Bar dataKey="value" name={data.metric} fill={chartColor(0)} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
