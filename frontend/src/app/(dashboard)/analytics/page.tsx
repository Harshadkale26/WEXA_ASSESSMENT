"use client";

import { Suspense } from "react";

import { AnalyticsDashboard } from "@/components/dashboard/analytics-dashboard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Spinner } from "@/components/ui/spinner";

export default function AnalyticsPage() {
  return (
    <DashboardShell title="Analytics">
      <Suspense
        fallback={
          <div className="flex min-h-[320px] items-center justify-center">
            <Spinner label="Loading" />
          </div>
        }
      >
        <AnalyticsDashboard />
      </Suspense>
    </DashboardShell>
  );
}
