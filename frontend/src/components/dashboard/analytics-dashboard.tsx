"use client";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import {
  DashboardError,
  DashboardLoading,
} from "@/components/dashboard/dashboard-page-state";
import { DashboardToolbar } from "@/components/dashboard/dashboard-toolbar";
import { EmptyDashboard } from "@/components/dashboard/empty-dashboard";
import { WidgetGrid } from "@/components/dashboard/widget-grid";
import { useDashboard, useDashboards } from "@/hooks/dashboard/use-dashboards";
import { useWidgetsData } from "@/hooks/dashboard/use-widget-data";
import { useAuthStore } from "@/stores/auth-store";
import type { TimeRangePreset } from "@/types/dashboard";
import type { Role } from "@/types/auth";

const BOOTSTRAP_ROLES: Role[] = ["owner", "admin", "analyst"];

function pickDashboardId(
  dashboards: { id: string; is_default: boolean }[],
  paramId: string | null
): string | null {
  if (paramId && dashboards.some((d) => d.id === paramId)) return paramId;
  const defaultDash = dashboards.find((d) => d.is_default);
  return defaultDash?.id ?? dashboards[0]?.id ?? null;
}

export function AnalyticsDashboard() {
  const searchParams = useSearchParams();
  const paramId = searchParams.get("id");

  const [timeRange, setTimeRange] = useState<TimeRangePreset>("7d");
  const userRole = useAuthStore((s) => s.user?.role);
  const canBootstrap = !!userRole && BOOTSTRAP_ROLES.includes(userRole);
  const [manualDashboardId, setManualDashboardId] = useState<string | null>(null);

  const dashboardsQuery = useDashboards();
  const dashboards = dashboardsQuery.data ?? [];

  const selectedId = useMemo(() => {
    if (manualDashboardId && dashboards.some((d) => d.id === manualDashboardId)) {
      return manualDashboardId;
    }
    return pickDashboardId(dashboards, paramId);
  }, [dashboards, paramId, manualDashboardId]);

  const dashboardQuery = useDashboard(selectedId);
  const widgets = useMemo(
    () =>
      [...(dashboardQuery.data?.widgets ?? [])].sort(
        (a, b) => a.sort_order - b.sort_order
      ),
    [dashboardQuery.data?.widgets]
  );
  const widgetQueries = useWidgetsData(widgets, timeRange);

  const isRefreshing =
    dashboardsQuery.isFetching ||
    dashboardQuery.isFetching ||
    widgetQueries.some((q) => q.isFetching);

  const lastUpdated = useMemo(() => {
    const times = widgetQueries
      .map((q) => q.dataUpdatedAt)
      .filter((t) => t > 0);
    if (!times.length) return dashboardQuery.dataUpdatedAt
      ? new Date(dashboardQuery.dataUpdatedAt)
      : null;
    return new Date(Math.max(...times));
  }, [widgetQueries, dashboardQuery.dataUpdatedAt]);

  if (dashboardsQuery.isLoading) {
    return <DashboardLoading />;
  }

  if (dashboardsQuery.isError) {
    return (
      <DashboardError error={dashboardsQuery.error} onRetry={() => dashboardsQuery.refetch()} />
    );
  }

  if (!dashboards.length) {
    return <EmptyDashboard hasDashboards={false} canBootstrap={canBootstrap} />;
  }

  if (!selectedId) {
    return <EmptyDashboard hasDashboards={true} />;
  }

  if (dashboardQuery.isLoading) {
    return (
      <div className="space-y-6">
        <DashboardToolbar
          dashboards={dashboards}
          selectedId={selectedId}
          onSelectDashboard={setManualDashboardId}
          timeRange={timeRange}
          onTimeRangeChange={setTimeRange}
          isRefreshing
        />
        <DashboardLoading />
      </div>
    );
  }

  if (dashboardQuery.isError) {
    return (
      <div className="space-y-6">
        <DashboardToolbar
          dashboards={dashboards}
          selectedId={selectedId}
          onSelectDashboard={setManualDashboardId}
          timeRange={timeRange}
          onTimeRangeChange={setTimeRange}
        />
        <DashboardError error={dashboardQuery.error} onRetry={() => dashboardQuery.refetch()} />
      </div>
    );
  }

  const dashboard = dashboardQuery.data!;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-foreground">{dashboard.name}</h2>
        {dashboard.description && (
          <p className="mt-1 text-sm text-muted">{dashboard.description}</p>
        )}
      </div>

      <DashboardToolbar
        dashboards={dashboards}
        selectedId={selectedId}
        onSelectDashboard={setManualDashboardId}
        timeRange={timeRange}
        onTimeRangeChange={setTimeRange}
        isRefreshing={isRefreshing}
        lastUpdated={lastUpdated}
      />

      {!widgets.length ? (
        <EmptyDashboard hasDashboards={true} canBootstrap={canBootstrap} />
      ) : (
        <WidgetGrid widgets={widgets} queries={widgetQueries} />
      )}
    </div>
  );
}
