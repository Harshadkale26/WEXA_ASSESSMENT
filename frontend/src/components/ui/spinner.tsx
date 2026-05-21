import { cn } from "@/lib/utils/cn";

export function Spinner({ className, label = "Loading" }: { className?: string; label?: string }) {
  return (
    <div className={cn("flex flex-col items-center gap-3", className)} role="status" aria-live="polite">
      <div
        className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-brand-600"
        aria-hidden
      />
      <span className="text-sm text-muted">{label}…</span>
    </div>
  );
}
