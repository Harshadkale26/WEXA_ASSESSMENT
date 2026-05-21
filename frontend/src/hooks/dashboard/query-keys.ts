import type { TimeRangePreset } from "@/types/dashboard";

export const dashboardKeys = {
  all: ["dashboards"] as const,
  list: () => [...dashboardKeys.all, "list"] as const,
  detail: (id: string) => [...dashboardKeys.all, "detail", id] as const,
  widgetData: (widgetId: string, timeRange: TimeRangePreset) =>
    [...dashboardKeys.all, "widget-data", widgetId, timeRange] as const,
};

export const DASHBOARD_REFETCH_MS = 30_000;
