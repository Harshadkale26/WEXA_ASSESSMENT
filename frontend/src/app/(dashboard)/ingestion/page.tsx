"use client";

import { DashboardShell } from "@/components/layout/dashboard-shell";

const ENDPOINTS = [
  {
    method: "POST",
    path: "/api/v1/ingestion/events",
    desc: "Single JSON event (X-API-Key)",
  },
  {
    method: "POST",
    path: "/api/v1/ingestion/events/batch",
    desc: "Batch JSON events",
  },
  {
    method: "POST",
    path: "/api/v1/ingestion/events/csv",
    desc: "CSV file upload",
  },
  {
    method: "POST",
    path: "/api/v1/ingestion/webhooks/events",
    desc: "Webhook receiver (optional X-Webhook-Signature HMAC-SHA256)",
  },
];

export default function IngestionPage() {
  return (
    <DashboardShell title="Event ingestion">
      <div className="max-w-3xl space-y-6">
        <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="font-semibold text-foreground">Data sources</h3>
          <ul className="mt-4 space-y-3">
            {ENDPOINTS.map((ep) => (
              <li key={ep.path} className="text-sm">
                <span className="font-mono font-medium text-brand-600">{ep.method}</span>{" "}
                <code className="rounded bg-muted-bg px-1.5 py-0.5 text-xs">{ep.path}</code>
                <p className="mt-1 text-muted">{ep.desc}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="font-semibold text-foreground">API keys</h3>
          <p className="mt-2 text-sm text-muted">
            Create, revoke, and rotate keys under{" "}
            <a href="/settings" className="font-medium text-brand-600 hover:underline">
              Settings
            </a>
            . Rate limits apply per organization and per API key.
          </p>
        </section>

        <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="font-semibold text-foreground">Webhook example</h3>
          <pre className="mt-3 overflow-x-auto rounded-lg bg-muted-bg p-4 text-xs text-foreground">
{`POST /api/v1/ingestion/webhooks/events
X-API-Key: <your-key>
X-Webhook-Signature: sha256=<hmac of raw body>
Content-Type: application/json

{
  "event_name": "order_placed",
  "event_type": "conversion",
  "source": "stripe-webhook",
  "timestamp": "2026-05-20T18:00:00Z",
  "payload": { "amount": 99 }
}`}
          </pre>
        </section>
      </div>
    </DashboardShell>
  );
}
