"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { dashboardKeys } from "@/hooks/dashboard/query-keys";
import { dashboardsApi } from "@/lib/api/dashboards";
import { parseApiError } from "@/lib/api/errors";
import { ROUTES } from "@/lib/constants";

export function EmptyDashboard({
  hasDashboards,
  canBootstrap = true,
}: {
  hasDashboards: boolean;
  canBootstrap?: boolean;
}) {
  const queryClient = useQueryClient();

  const bootstrap = useMutation({
    mutationFn: dashboardsApi.bootstrap,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
    },
  });

  return (
    <div className="rounded-xl border border-dashed border-border bg-surface p-10 text-center shadow-card">
      <h3 className="text-lg font-semibold text-foreground">
        {hasDashboards ? "No widgets on this dashboard" : "No dashboards yet"}
      </h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-muted">
        {hasDashboards
          ? "This dashboard has no widgets. Create a sample layout to visualize ingested events."
          : "Ingest events with your API key, then create a dashboard with charts."}
      </p>

      {canBootstrap && (
        <div className="mt-6 flex flex-col items-center gap-3">
          <Button
            type="button"
            onClick={() => bootstrap.mutate()}
            loading={bootstrap.isPending}
          >
            Create sample dashboard
          </Button>
          <p className="text-xs text-muted">
            Adds Overview dashboard with KPI, line, bar, and pie widgets (7-day range).
          </p>
        </div>
      )}

      {bootstrap.isError && (
        <Alert variant="error" className="mt-4 text-left">
          {parseApiError(bootstrap.error).message}
        </Alert>
      )}

      <p className="mt-6 text-xs text-muted">
        After creating widgets, set time range to <strong>7 days</strong> if your test events are
        older than 24 hours.
      </p>
      <Link
        href={ROUTES.dashboards}
        className="mt-4 inline-block text-sm font-medium text-brand-600 hover:underline"
      >
        View all dashboards →
      </Link>
    </div>
  );
}
