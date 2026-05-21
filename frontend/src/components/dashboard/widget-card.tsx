"use client";

import { cn } from "@/lib/utils/cn";
import type { UseQueryResult } from "@tanstack/react-query";

import { WidgetRenderer } from "@/components/dashboard/widget-renderer";
import { WidgetError } from "@/components/dashboard/widget-error";
import { WidgetSkeleton } from "@/components/dashboard/widget-skeleton";
import type { Widget, WidgetDataResponse } from "@/types/dashboard";

export function WidgetCard({
  widget,
  query,
}: {
  widget: Widget;
  query: UseQueryResult<WidgetDataResponse, Error>;
}) {
  const isKpi = widget.widget_type === "kpi_card";

  return (
    <article
      className={cn(
        "flex h-full flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-card",
        isKpi && "min-h-[140px]"
      )}
    >
      <header className="flex shrink-0 items-center justify-between border-b border-border px-4 py-3">
        <h3 className="truncate text-sm font-semibold text-foreground">{widget.title}</h3>
        <span className="shrink-0 rounded-md bg-muted-bg px-2 py-0.5 text-xs capitalize text-muted">
          {widget.widget_type.replace("_", " ")}
        </span>
      </header>
      <div className={cn("relative flex-1", isKpi ? "p-4" : "min-h-[220px] p-2 pb-4")}>
        {query.isLoading && <WidgetSkeleton />}
        {query.isError && !query.isLoading && (
          <WidgetError error={query.error} onRetry={() => query.refetch()} />
        )}
        {query.isSuccess && query.data && <WidgetRenderer data={query.data} />}
      </div>
    </article>
  );
}
