"use client";

import { useQuery } from "@tanstack/react-query";

import { authKeys } from "@/hooks/auth/query-keys";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth-store";

export function useSession() {
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const accessToken = useAuthStore((s) => s.accessToken);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const user = useAuthStore((s) => s.user);

  const query = useQuery({
    queryKey: authKeys.me,
    queryFn: authApi.me,
    enabled: isHydrated && !!accessToken && isAuthenticated,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  return {
    user: query.data ?? user,
    isLoading: !isHydrated || (isAuthenticated && query.isLoading),
    isError: query.isError,
    refetch: query.refetch,
  };
}
