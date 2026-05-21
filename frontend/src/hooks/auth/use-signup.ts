"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { authApi } from "@/lib/api/auth";
import { parseApiError } from "@/lib/api/errors";
import { ROUTES } from "@/lib/constants";
import type { SignupFormValues } from "@/lib/validations/auth";
import { useAuthStore } from "@/stores/auth-store";

export function useSignup() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: (values: SignupFormValues) => {
      const { confirm_password: _confirm, ...payload } = values;
      return authApi.signup(payload);
    },
    onSuccess: (data) => {
      setAuth(data);
      router.push(ROUTES.dashboard);
    },
    meta: {
      getErrorMessage: (error: unknown) => parseApiError(error).message,
    },
  });
}
