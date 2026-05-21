import { cn } from "@/lib/utils/cn";

export function AuthCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-surface p-8 shadow-card",
        className
      )}
    >
      {children}
    </div>
  );
}
