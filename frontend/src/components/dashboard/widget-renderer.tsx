"use client";

import { BarChartWidget } from "@/components/dashboard/charts/bar-chart-widget";
import { KpiChart } from "@/components/dashboard/charts/kpi-chart";
import { LineChartWidget } from "@/components/dashboard/charts/line-chart-widget";
import { PieChartWidget } from "@/components/dashboard/charts/pie-chart-widget";
import type { WidgetDataResponse } from "@/types/dashboard";

export function WidgetRenderer({ data }: { data: WidgetDataResponse }) {
  switch (data.widget_type) {
    case "kpi_card":
      return <KpiChart data={data} />;
    case "line_chart":
      return <LineChartWidget data={data} />;
    case "bar_chart":
      return <BarChartWidget data={data} />;
    case "pie_chart":
      return <PieChartWidget data={data} />;
    default:
      return <p className="text-sm text-muted">Unsupported widget type</p>;
  }
}
