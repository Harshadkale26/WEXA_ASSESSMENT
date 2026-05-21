"use client";

import { useLogout } from "@/hooks/auth/use-logout";
import { useSession } from "@/hooks/auth/use-session";
import { useAuthStore } from "@/stores/auth-store";

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const organization = useAuthStore((s) => s.organization);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const isInitializing = useAuthStore((s) => s.isInitializing);
  const accessToken = useAuthStore((s) => s.accessToken);
  const session = useSession();
  const logout = useLogout();

  return {
    user: session.user ?? user,
    organization,
    isAuthenticated,
    isHydrated,
    isInitializing,
    accessToken,
    isSessionLoading: session.isLoading,
    logout,
  };
}
