import { publicApi } from "@/lib/api/public-client";
import { authStore } from "@/stores/auth-store";
import type { TokenResponse } from "@/types/auth";

export async function refreshAccessToken(): Promise<TokenResponse> {
  const refreshToken = authStore.getState().refreshToken;
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  const { data } = await publicApi.post<TokenResponse>("/auth/refresh", {
    refresh_token: refreshToken,
  });

  authStore.getState().updateTokens(data);
  return data;
}
