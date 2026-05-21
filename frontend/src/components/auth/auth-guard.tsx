"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Spinner } from "@/components/ui/spinner";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth-store";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const isInitializing = useAuthStore((s) => s.isInitializing);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const accessToken = useAuthStore((s) => s.accessToken);

  const ready = isHydrated && !isInitializing;
  const allowed = isAuthenticated || !!accessToken;

  useEffect(() => {
    if (ready && !allowed) {
      router.replace(ROUTES.login);
    }
  }, [ready, allowed, router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Spinner label="Restoring session" />
      </div>
    );
  }

  if (!allowed) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Spinner label="Redirecting to sign in" />
      </div>
    );
  }

  return <>{children}</>;
}
