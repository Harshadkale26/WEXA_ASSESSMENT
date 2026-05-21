"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";

import { authApi } from "@/lib/api/auth";
import { parseApiError } from "@/lib/api/errors";
import { ROUTES } from "@/lib/constants";
import type { LoginFormValues } from "@/lib/validations/auth";
import { useAuthStore } from "@/stores/auth-store";

export function useLogin() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: (values: LoginFormValues) => authApi.login(values),
    onSuccess: (data) => {
      setAuth(data);
      const from = searchParams.get("from");
      const destination =
        from && from.startsWith("/") && !from.startsWith("//") ? from : ROUTES.dashboard;
      router.push(destination);
    },
    meta: {
      getErrorMessage: (error: unknown) => parseApiError(error).message,
    },
  });
}
