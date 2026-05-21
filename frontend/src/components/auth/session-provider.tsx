"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, type ReactNode } from "react";

import { authKeys } from "@/hooks/auth/query-keys";
import { authApi } from "@/lib/api/auth";
import { refreshAccessToken } from "@/lib/api/refresh-token";
import { isTokenExpiringSoon } from "@/lib/auth/tokens";
import { useAuthStore } from "@/stores/auth-store";

const PROACTIVE_REFRESH_BUFFER_MS = 120_000;
const REFRESH_CHECK_INTERVAL_MS = 30_000;

export function SessionProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const accessToken = useAuthStore((s) => s.accessToken);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const tokenExpiresAt = useAuthStore((s) => s.tokenExpiresAt);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const setUser = useAuthStore((s) => s.setUser);
  const setInitializing = useAuthStore((s) => s.setInitializing);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const syncCookie = useAuthStore((s) => s.syncCookie);

  useEffect(() => {
    if (isHydrated) syncCookie();
  }, [isHydrated, syncCookie]);

  useEffect(() => {
    if (!isHydrated) return;

    let cancelled = false;

    async function bootstrap() {
      const state = useAuthStore.getState();
      const hasSession = !!(state.accessToken || state.refreshToken);
      if (!hasSession) return;

      setInitializing(true);
      try {
        if (
          state.refreshToken &&
          (!state.accessToken ||
            isTokenExpiringSoon(state.tokenExpiresAt, PROACTIVE_REFRESH_BUFFER_MS))
        ) {
          await refreshAccessToken();
        }
        if (!cancelled) {
          await queryClient.prefetchQuery({
            queryKey: authKeys.me,
            queryFn: authApi.me,
          });
        }
      } catch {
        if (!cancelled) clearAuth();
      } finally {
        if (!cancelled) setInitializing(false);
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, [isHydrated, queryClient, setInitializing, clearAuth]);

  const { data } = useQuery({
    queryKey: authKeys.me,
    queryFn: authApi.me,
    enabled: isHydrated && !!accessToken && isAuthenticated,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  useEffect(() => {
    if (data) setUser(data);
  }, [data, setUser]);

  useEffect(() => {
    if (!isHydrated || !refreshToken || !tokenExpiresAt) return;

    const interval = setInterval(() => {
      if (isTokenExpiringSoon(tokenExpiresAt, PROACTIVE_REFRESH_BUFFER_MS)) {
        refreshAccessToken().catch(() => clearAuth());
      }
    }, REFRESH_CHECK_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [isHydrated, refreshToken, tokenExpiresAt, clearAuth]);

  return <>{children}</>;
}
