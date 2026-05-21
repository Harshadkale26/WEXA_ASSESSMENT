import { api } from "@/lib/api/client";
import { publicApi } from "@/lib/api/public-client";
import type {
  ApiKeyListItem,
  AuthResponse,
  CreateApiKeyPayload,
  CreateApiKeyResponse,
  LoginPayload,
  SignupPayload,
  TokenResponse,
  User,
} from "@/types/auth";

export const authApi = {
  signup: (payload: SignupPayload) =>
    publicApi.post<AuthResponse>("/auth/signup", payload).then((r) => r.data),

  login: (payload: LoginPayload) =>
    publicApi.post<AuthResponse>("/auth/login", payload).then((r) => r.data),

  refresh: (refresh_token: string) =>
    publicApi
      .post<TokenResponse>("/auth/refresh", { refresh_token })
      .then((r) => r.data),

  me: () => api.get<User>("/auth/me").then((r) => r.data),

  listApiKeys: () => api.get<ApiKeyListItem[]>("/auth/api-keys").then((r) => r.data),

  createApiKey: (payload: CreateApiKeyPayload) =>
    api.post<CreateApiKeyResponse>("/auth/api-keys", payload).then((r) => r.data),

  revokeApiKey: (keyId: string) =>
    api.post<ApiKeyListItem>(`/auth/api-keys/${keyId}/revoke`).then((r) => r.data),

  rotateApiKey: (keyId: string) =>
    api.post<CreateApiKeyResponse>(`/auth/api-keys/${keyId}/rotate`).then((r) => r.data),
};
