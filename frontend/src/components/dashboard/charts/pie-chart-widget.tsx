"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { chartColor } from "@/components/dashboard/chart-colors";
import { ChartTooltipContent } from "@/components/dashboard/charts/chart-tooltip";
import type { WidgetDataResponse } from "@/types/dashboard";

function toChartData(data: WidgetDataResponse) {
  return data.points.map((p) => ({
    name: p.label,
    value: p.value,
  }));
}

export function PieChartWidget({ data }: { data: WidgetDataResponse }) {
  const chartData = toChartData(data);

  if (!chartData.length) {
    return <p className="py-8 text-center text-sm text-muted">No data for this period</p>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%" minHeight={220}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius="52%"
          outerRadius="78%"
          paddingAngle={2}
        >
          {chartData.map((_, index) => (
            <Cell key={index} fill={chartColor(index)} />
          ))}
        </Pie>
        <Tooltip content={<ChartTooltipContent />} />
      </PieChart>
    </ResponsiveContainer>
  );
}
