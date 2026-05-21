"use client";

import { cn } from "@/lib/utils/cn";
import type { TimeRangePreset } from "@/types/dashboard";

const PRESETS: { value: TimeRangePreset; label: string }[] = [
  { value: "1h", label: "1 hour" },
  { value: "24h", label: "24 hours" },
  { value: "7d", label: "7 days" },
  { value: "30d", label: "30 days" },
];

export function TimeRangeSelector({
  value,
  onChange,
  className,
}: {
  value: TimeRangePreset;
  onChange: (preset: TimeRangePreset) => void;
  className?: string;
}) {
  return (
    <div
      className={cn("inline-flex flex-wrap gap-1 rounded-lg border border-border bg-surface p-1", className)}
      role="group"
      aria-label="Time range"
    >
      {PRESETS.map((preset) => (
        <button
          key={preset.value}
          type="button"
          onClick={() => onChange(preset.value)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm font-medium transition",
            value === preset.value
              ? "bg-brand-600 text-white shadow-sm"
              : "text-muted hover:bg-muted-bg hover:text-foreground"
          )}
        >
          {preset.label}
        </button>
      ))}
    </div>
  );
}
