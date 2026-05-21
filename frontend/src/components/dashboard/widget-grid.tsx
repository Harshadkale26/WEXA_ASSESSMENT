"use client";

import type { UseQueryResult } from "@tanstack/react-query";

import { WidgetCard } from "@/components/dashboard/widget-card";
import type { Widget, WidgetDataResponse, WidgetLayout } from "@/types/dashboard";

const DEFAULT_LAYOUT: WidgetLayout = { x: 0, y: 0, w: 4, h: 3 };
const COLS = 12;

function resolveLayout(
  layout: WidgetLayout | null,
  index: number,
  isKpi: boolean
): WidgetLayout {
  if (layout) return layout;
  return {
    x: (index % 3) * 4,
    y: Math.floor(index / 3) * 3,
    w: 4,
    h: isKpi ? 2 : 3,
  };
}

export function WidgetGrid({
  widgets,
  queries,
}: {
  widgets: Widget[];
  queries: UseQueryResult<WidgetDataResponse, Error>[];
}) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-12 xl:auto-rows-min">
      {widgets.map((widget, index) => {
        const isKpi = widget.widget_type === "kpi_card";
        const l = resolveLayout(widget.layout, index, isKpi);
        return (
          <div
            key={widget.id}
            className="min-w-0 xl:[grid-column:var(--widget-col)] xl:[grid-row:var(--widget-row)]"
            style={
              {
                ["--widget-col" as string]: `${Math.min(l.x + 1, COLS)} / span ${Math.min(l.w, COLS)}`,
                ["--widget-row" as string]: `span ${l.h}`,
                minHeight: `${l.h * 80}px`,
              } as React.CSSProperties
            }
          >
            <WidgetCard widget={widget} query={queries[index]} />
          </div>
        );
      })}
    </div>
  );
}
