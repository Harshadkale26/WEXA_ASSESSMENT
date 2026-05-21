"use client";

import { Button } from "@/components/ui/button";
import { parseApiError } from "@/lib/api/errors";

export function WidgetError({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  const message = parseApiError(error).message;
  return (
    <div className="flex h-full min-h-[140px] flex-col items-center justify-center gap-3 p-4 text-center">
      <p className="text-sm font-medium text-red-700">Failed to load widget</p>
      <p className="max-w-xs text-xs text-muted">{message}</p>
      {onRetry && (
        <Button type="button" variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}
