"use client";

import Link from "next/link";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useDashboards } from "@/hooks/dashboard/use-dashboards";
import { parseApiError } from "@/lib/api/errors";
import { ROUTES } from "@/lib/constants";

export default function DashboardsListPage() {
  const { data, isLoading, isError, error, refetch, isFetching } = useDashboards();

  return (
    <DashboardShell title="Dashboards">
      <div className="space-y-6">
        <p className="text-sm text-muted">
          Select a dashboard to view widgets and charts. Data refreshes every 30 seconds.
        </p>

        {isLoading && (
          <div className="flex justify-center py-12">
            <Spinner label="Loading dashboards" />
          </div>
        )}

        {isError && (
          <div className="space-y-4">
            <Alert variant="error" title="Failed to load dashboards">
              {parseApiError(error).message}
            </Alert>
            <Button type="button" variant="secondary" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        )}

        {data && data.length === 0 && (
          <div className="rounded-xl border border-dashed border-border bg-surface p-8 text-center">
            <p className="text-muted">No dashboards found for your organization.</p>
          </div>
        )}

        {data && data.length > 0 && (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((dashboard) => (
              <li key={dashboard.id}>
                <Link
                  href={`${ROUTES.dashboard}?id=${dashboard.id}`}
                  className="block rounded-xl border border-border bg-surface p-5 shadow-card transition hover:border-brand-500 hover:shadow-md"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-foreground">{dashboard.name}</h3>
                    {dashboard.is_default && (
                      <span className="shrink-0 rounded bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-600">
                        Default
                      </span>
                    )}
                  </div>
                  {dashboard.description && (
                    <p className="mt-2 line-clamp-2 text-sm text-muted">{dashboard.description}</p>
                  )}
                  <p className="mt-4 text-xs text-muted">
                    Updated {new Date(dashboard.updated_at).toLocaleDateString()}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}

        {isFetching && !isLoading && (
          <p className="text-center text-xs text-muted">Refreshing…</p>
        )}
      </div>
    </DashboardShell>
  );
}
