"use client";

import { useAuth } from "@/hooks/use-auth";

export function Header({ title }: { title: string }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-surface px-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        {user && (
          <p className="text-sm text-muted">Welcome back, {user.full_name}</p>
        )}
      </div>
      <button
        type="button"
        onClick={logout}
        className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground transition hover:bg-muted-bg"
      >
        Sign out
      </button>
    </header>
  );
}
