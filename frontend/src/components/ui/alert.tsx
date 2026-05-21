import { cn } from "@/lib/utils/cn";

type AlertVariant = "error" | "success" | "info";

const variantStyles: Record<AlertVariant, string> = {
  error: "border-red-200 bg-red-50 text-red-800",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  info: "border-brand-200 bg-brand-50 text-brand-900",
};

export function Alert({
  children,
  variant = "error",
  className,
  title,
}: {
  children: React.ReactNode;
  variant?: AlertVariant;
  className?: string;
  title?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-lg border px-3 py-2.5 text-sm",
        variantStyles[variant],
        className
      )}
    >
      {title && <p className="mb-1 font-medium">{title}</p>}
      {children}
    </div>
  );
}
