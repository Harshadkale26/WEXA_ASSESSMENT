"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils/cn";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth-store";

const navItems = [
  { href: ROUTES.dashboard, label: "Overview", icon: "◉" },
  { href: ROUTES.analytics, label: "Analytics", icon: "▣" },
  { href: ROUTES.dashboards, label: "Dashboards", icon: "▦" },
  { href: ROUTES.ingestion, label: "Ingestion", icon: "↑" },
  { href: ROUTES.settings, label: "Settings", icon: "⚙" },
];

export function Sidebar() {
  const pathname = usePathname();
  const organization = useAuthStore((s) => s.organization);
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      <div className="border-b border-sidebar-border px-5 py-6">
        <p className="text-xs font-medium uppercase tracking-wider text-sidebar-muted">
          Analytics
        </p>
        <h1 className="mt-1 truncate text-lg font-semibold text-white">
          {organization?.name ?? "Platform"}
        </h1>
        {user && (
          <p className="mt-1 truncate text-sm text-sidebar-muted">{user.email}</p>
        )}
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-sidebar-accent text-white"
                  : "text-sidebar-muted hover:bg-sidebar-accent/60 hover:text-white"
              )}
            >
              <span className="text-base opacity-80">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-sidebar-border px-5 py-4 text-xs text-sidebar-muted">
        Role: {user?.role ?? "—"}
      </div>
    </aside>
  );
}
