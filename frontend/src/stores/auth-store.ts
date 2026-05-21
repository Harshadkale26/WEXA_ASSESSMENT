"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import {
  clearAccessTokenCookie,
  computeExpiresAt,
  getAccessTokenCookie,
  setAccessTokenCookie,
} from "@/lib/auth/tokens";
import type { AuthResponse, Organization, TokenResponse, User } from "@/types/auth";

interface AuthState {
  user: User | null;
  organization: Organization | null;
  accessToken: string | null;
  refreshToken: string | null;
  tokenExpiresAt: number | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  isInitializing: boolean;

  setAuth: (payload: AuthResponse) => void;
  updateTokens: (tokens: TokenResponse) => void;
  setUser: (user: User) => void;
  clearAuth: () => void;
  setHydrated: (value: boolean) => void;
  setInitializing: (value: boolean) => void;
  syncCookie: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      organization: null,
      accessToken: null,
      refreshToken: null,
      tokenExpiresAt: null,
      isAuthenticated: false,
      isHydrated: false,
      isInitializing: false,

      setAuth: (payload) => {
        const expiresAt = computeExpiresAt(payload.tokens.expires_in);
        setAccessTokenCookie(payload.tokens.access_token, payload.tokens.expires_in);
        set({
          user: payload.user,
          organization: payload.organization,
          accessToken: payload.tokens.access_token,
          refreshToken: payload.tokens.refresh_token,
          tokenExpiresAt: expiresAt,
          isAuthenticated: true,
        });
      },

      updateTokens: (tokens) => {
        const expiresAt = computeExpiresAt(tokens.expires_in);
        setAccessTokenCookie(tokens.access_token, tokens.expires_in);
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          tokenExpiresAt: expiresAt,
          isAuthenticated: true,
        });
      },

      setUser: (user) => set({ user }),

      clearAuth: () => {
        clearAccessTokenCookie();
        set({
          user: null,
          organization: null,
          accessToken: null,
          refreshToken: null,
          tokenExpiresAt: null,
          isAuthenticated: false,
          isInitializing: false,
        });
      },

      setHydrated: (value) => set({ isHydrated: value }),

      setInitializing: (value) => set({ isInitializing: value }),

      syncCookie: () => {
        const cookieToken = getAccessTokenCookie();
        const { accessToken, user } = get();
        if (cookieToken && accessToken && cookieToken === accessToken) {
          set({ isAuthenticated: true });
        } else if (cookieToken && user) {
          set({ accessToken: cookieToken, isAuthenticated: true });
        } else if (!cookieToken && accessToken) {
          setAccessTokenCookie(accessToken);
          set({ isAuthenticated: !!user });
        }
      },
    }),
    {
      name: "analytics-auth",
      partialize: (state) => ({
        user: state.user,
        organization: state.organization,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        tokenExpiresAt: state.tokenExpiresAt,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
        state?.syncCookie();
      },
    }
  )
);

export const authStore = {
  getState: () => useAuthStore.getState(),
};
