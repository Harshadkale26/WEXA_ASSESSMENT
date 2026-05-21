"use client";

import { TimeRangeSelector } from "@/components/dashboard/time-range-selector";
import type { Dashboard, TimeRangePreset } from "@/types/dashboard";

export function DashboardToolbar({
  dashboards,
  selectedId,
  onSelectDashboard,
  timeRange,
  onTimeRangeChange,
  isRefreshing,
  lastUpdated,
}: {
  dashboards: Dashboard[];
  selectedId: string | null;
  onSelectDashboard: (id: string) => void;
  timeRange: TimeRangePreset;
  onTimeRangeChange: (preset: TimeRangePreset) => void;
  isRefreshing?: boolean;
  lastUpdated?: Date | null;
}) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        {dashboards.length > 1 && (
          <label className="flex items-center gap-2 text-sm">
            <span className="font-medium text-muted">Dashboard</span>
            <select
              value={selectedId ?? ""}
              onChange={(e) => onSelectDashboard(e.target.value)}
              className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {dashboards.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                  {d.is_default ? " (default)" : ""}
                </option>
              ))}
            </select>
          </label>
        )}
        <TimeRangeSelector value={timeRange} onChange={onTimeRangeChange} />
      </div>
      <div className="flex items-center gap-2 text-xs text-muted">
        <span
          className={`inline-block h-2 w-2 rounded-full ${isRefreshing ? "animate-pulse bg-brand-500" : "bg-emerald-500"}`}
          aria-hidden
        />
        <span>
          Auto-refresh every 30s
          {lastUpdated ? ` · Updated ${lastUpdated.toLocaleTimeString()}` : ""}
        </span>
      </div>
    </div>
  );
}
