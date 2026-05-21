"use client";

import { useQuery } from "@tanstack/react-query";

import { DASHBOARD_REFETCH_MS, dashboardKeys } from "@/hooks/dashboard/query-keys";
import { dashboardsApi } from "@/lib/api/dashboards";

export function useDashboards() {
  return useQuery({
    queryKey: dashboardKeys.list(),
    queryFn: dashboardsApi.list,
    staleTime: 60_000,
    refetchInterval: DASHBOARD_REFETCH_MS,
  });
}

export function useDashboard(dashboardId: string | null) {
  return useQuery({
    queryKey: dashboardKeys.detail(dashboardId ?? ""),
    queryFn: () => dashboardsApi.get(dashboardId!),
    enabled: !!dashboardId,
    staleTime: 30_000,
    refetchInterval: DASHBOARD_REFETCH_MS,
  });
}
