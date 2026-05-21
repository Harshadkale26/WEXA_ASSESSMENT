import { cn } from "@/lib/utils/cn";
import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", loading, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-medium transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:opacity-50",
          variant === "primary" && "bg-brand-600 text-white hover:bg-brand-500",
          variant === "secondary" &&
            "border border-border bg-surface text-foreground hover:bg-muted-bg",
          variant === "ghost" && "text-foreground hover:bg-muted-bg",
          className
        )}
        {...props}
      >
        {loading ? "Loading…" : children}
      </button>
    );
  }
);
Button.displayName = "Button";
