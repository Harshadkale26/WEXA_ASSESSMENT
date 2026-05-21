"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { authApi } from "@/lib/api/auth";
import { parseApiError } from "@/lib/api/errors";
import type { ApiKeyListItem, CreateApiKeyResponse, Role } from "@/types/auth";

const ADMIN_ROLES: Role[] = ["owner", "admin"];

export function ApiKeysSection({ role }: { role?: Role }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("ingestion-test");
  const [createdKey, setCreatedKey] = useState<CreateApiKeyResponse | null>(null);
  const [copied, setCopied] = useState<"key" | "webhook" | null>(null);

  const keysQuery = useQuery({
    queryKey: ["auth", "api-keys"],
    queryFn: authApi.listApiKeys,
    enabled: !!role && ADMIN_ROLES.includes(role),
  });

  const createKey = useMutation({
    mutationFn: () => authApi.createApiKey({ name: name.trim() || "default" }),
    onSuccess: (data) => {
      setCreatedKey(data);
      setCopied(null);
      queryClient.invalidateQueries({ queryKey: ["auth", "api-keys"] });
    },
  });

  const revokeKey = useMutation({
    mutationFn: (id: string) => authApi.revokeApiKey(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["auth", "api-keys"] }),
  });

  const rotateKey = useMutation({
    mutationFn: (id: string) => authApi.rotateApiKey(id),
    onSuccess: (data) => {
      setCreatedKey(data);
      setCopied(null);
      queryClient.invalidateQueries({ queryKey: ["auth", "api-keys"] });
    },
  });

  if (!role || !ADMIN_ROLES.includes(role)) {
    return (
      <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
        <h3 className="font-semibold text-foreground">API keys</h3>
        <p className="mt-2 text-sm text-muted">
          Only organization owners and admins can manage ingestion API keys. Your role:{" "}
          <span className="font-medium capitalize text-foreground">{role ?? "unknown"}</span>.
        </p>
      </section>
    );
  }

  const copyText = async (text: string, kind: "key" | "webhook") => {
    await navigator.clipboard.writeText(text);
    setCopied(kind);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <section className="rounded-xl border border-border bg-surface p-6 shadow-card">
      <h3 className="font-semibold text-foreground">API keys (ingestion)</h3>
      <p className="mt-2 text-sm text-muted">
        Use <code className="rounded bg-muted-bg px-1 text-xs">X-API-Key</code> for REST, CSV, and
        webhook ingestion. Webhooks also support{" "}
        <code className="rounded bg-muted-bg px-1 text-xs">X-Webhook-Signature</code> (HMAC-SHA256).
      </p>

      {keysQuery.data && keysQuery.data.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-muted">
                <th className="py-2 pr-4 font-medium">Name</th>
                <th className="py-2 pr-4 font-medium">Prefix</th>
                <th className="py-2 pr-4 font-medium">Status</th>
                <th className="py-2 pr-4 font-medium">Webhook</th>
                <th className="py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {keysQuery.data.map((key: ApiKeyListItem) => (
                <tr key={key.id} className="border-b border-border/60">
                  <td className="py-3 pr-4 text-foreground">{key.name}</td>
                  <td className="py-3 pr-4 font-mono text-xs">{key.key_prefix}</td>
                  <td className="py-3 pr-4">
                    <span
                      className={
                        key.is_active
                          ? "text-emerald-700"
                          : "text-muted line-through"
                      }
                    >
                      {key.is_active ? "Active" : "Revoked"}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-muted">
                    {key.has_webhook_signing_secret ? "Yes" : "—"}
                  </td>
                  <td className="py-3">
                    <div className="flex flex-wrap gap-2">
                      {key.is_active && (
                        <>
                          <Button
                            type="button"
                            variant="secondary"
                            onClick={() => rotateKey.mutate(key.id)}
                            loading={rotateKey.isPending}
                          >
                            Rotate
                          </Button>
                          <Button
                            type="button"
                            variant="ghost"
                            onClick={() => revokeKey.mutate(key.id)}
                            loading={revokeKey.isPending}
                          >
                            Revoke
                          </Button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!createdKey ? (
        <form
          className="mt-6 space-y-4 border-t border-border pt-6"
          onSubmit={(e) => {
            e.preventDefault();
            createKey.mutate();
          }}
        >
          <h4 className="text-sm font-semibold text-foreground">Create new key</h4>
          <Input
            label="Key name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="ingestion-test"
          />
          {createKey.isError && (
            <Alert variant="error">{parseApiError(createKey.error).message}</Alert>
          )}
          <Button type="submit" loading={createKey.isPending}>
            Create API key
          </Button>
        </form>
      ) : (
        <div className="mt-6 space-y-4 border-t border-border pt-6">
          <Alert variant="info" title="Copy secrets now">
            API key and webhook signing secret are shown only once.
          </Alert>
          <div className="space-y-2">
            <p className="text-sm font-medium text-foreground">API key</p>
            <pre className="overflow-x-auto rounded-lg border border-border bg-muted-bg p-3 text-xs">
              {createdKey.api_key}
            </pre>
            <Button type="button" onClick={() => copyText(createdKey.api_key, "key")}>
              {copied === "key" ? "Copied" : "Copy API key"}
            </Button>
          </div>
          {createdKey.webhook_signing_secret && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-foreground">Webhook signing secret</p>
              <pre className="overflow-x-auto rounded-lg border border-border bg-muted-bg p-3 text-xs">
                {createdKey.webhook_signing_secret}
              </pre>
              <Button
                type="button"
                variant="secondary"
                onClick={() => copyText(createdKey.webhook_signing_secret!, "webhook")}
              >
                {copied === "webhook" ? "Copied" : "Copy webhook secret"}
              </Button>
            </div>
          )}
          <Button
            type="button"
            variant="secondary"
            onClick={() => {
              setCreatedKey(null);
              createKey.reset();
              rotateKey.reset();
            }}
          >
            Done
          </Button>
        </div>
      )}

      {(revokeKey.isError || rotateKey.isError) && (
        <Alert variant="error" className="mt-4">
          {parseApiError(revokeKey.error ?? rotateKey.error).message}
        </Alert>
      )}
    </section>
  );
}
