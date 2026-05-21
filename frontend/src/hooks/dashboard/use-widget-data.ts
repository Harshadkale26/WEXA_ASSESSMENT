"use client";

import { useQueries } from "@tanstack/react-query";

import { DASHBOARD_REFETCH_MS, dashboardKeys } from "@/hooks/dashboard/query-keys";
import { widgetsApi } from "@/lib/api/dashboards";
import type { TimeRangePreset, Widget } from "@/types/dashboard";

export function useWidgetsData(widgets: Widget[], timeRange: TimeRangePreset) {
  return useQueries({
    queries: widgets.map((widget) => ({
      queryKey: dashboardKeys.widgetData(widget.id, timeRange),
      queryFn: () =>
        widgetsApi.getData(widget.id, {
          time_range: { preset: timeRange },
        }),
      enabled: !!widget.id,
      staleTime: 15_000,
      refetchInterval: DASHBOARD_REFETCH_MS,
      retry: 1,
    })),
  });
}
