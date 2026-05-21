"use client";

import { useQuery } from "@tanstack/react-query";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ApiKeysSection } from "@/components/settings/api-keys-section";
import { authKeys } from "@/hooks/auth/query-keys";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth-store";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const org = useAuthStore((s) => s.organization);

  const { data: me, isLoading } = useQuery({
    queryKey: authKeys.me,
    queryFn: authApi.me,
    enabled: !!user,
  });

  return (
    <DashboardShell title="Settings">
      <div className="max-w-xl space-y-6">
        <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="font-semibold text-foreground">Profile</h3>
          {isLoading ? (
            <p className="mt-4 text-sm text-muted">Loading…</p>
          ) : (
            <dl className="mt-4 space-y-3 text-sm">
              <Row label="Name" value={me?.full_name ?? user?.full_name} />
              <Row label="Email" value={me?.email ?? user?.email} />
              <Row label="Role" value={me?.role ?? user?.role} />
            </dl>
          )}
        </section>
        <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="font-semibold text-foreground">Organization</h3>
          <dl className="mt-4 space-y-3 text-sm">
            <Row label="Name" value={org?.name} />
            <Row label="Slug" value={org?.slug} />
          </dl>
        </section>
        <ApiKeysSection role={me?.role ?? user?.role} />
      </div>
    </DashboardShell>
  );
}

function Row({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-muted">{label}</dt>
      <dd className="font-medium text-foreground">{value ?? "—"}</dd>
    </div>
  );
}
