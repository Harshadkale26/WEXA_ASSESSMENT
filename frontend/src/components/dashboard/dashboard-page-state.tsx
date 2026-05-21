"use client";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { parseApiError } from "@/lib/api/errors";

export function DashboardLoading() {
  return (
    <div className="flex min-h-[320px] items-center justify-center">
      <Spinner label="Loading dashboard" />
    </div>
  );
}

export function DashboardError({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry: () => void;
}) {
  const message = parseApiError(error).message;
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center gap-4">
      <Alert variant="error" title="Could not load dashboard">
        {message}
      </Alert>
      <Button type="button" variant="secondary" onClick={onRetry}>
        Try again
      </Button>
    </div>
  );
}
