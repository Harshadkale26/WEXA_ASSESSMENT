"use client";

import { Alert } from "@/components/ui/alert";
import { parseApiError } from "@/lib/api/errors";

export function AuthAlert({ error }: { error: unknown }) {
  if (!error) return null;
  const message = parseApiError(error).message;
  return (
    <Alert variant="error" title="Unable to continue">
      {message}
    </Alert>
  );
}
