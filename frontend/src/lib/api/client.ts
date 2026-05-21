import axios, {
  type AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";

import { parseApiError } from "@/lib/api/errors";
import { refreshAccessToken } from "@/lib/api/refresh-token";
import { getAccessTokenCookie } from "@/lib/auth/tokens";
import { API_PREFIX } from "@/lib/constants";
import { config } from "@/lib/config";
import { authStore } from "@/stores/auth-store";
export const api = axios.create({
  baseURL: `${config.apiUrl}${API_PREFIX}`,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

const AUTH_SKIP_REFRESH = ["/auth/login", "/auth/signup", "/auth/refresh"];

function shouldAttemptRefresh(url?: string): boolean {
  if (!url) return true;
  return !AUTH_SKIP_REFRESH.some((path) => url.includes(path));
}

function getAccessToken(): string | null {
  return authStore.getState().accessToken ?? getAccessTokenCookie() ?? null;
}

api.interceptors.request.use((req: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token && req.headers) {
    req.headers.Authorization = `Bearer ${token}`;
  }
  return req;
});

let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processRefreshQueue(error: unknown | null, token: string | null = null) {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else if (token) resolve(token);
  });
  refreshQueue = [];
}

function redirectToLogin() {
  authStore.getState().clearAuth();
  if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
    const from = window.location.pathname;
    const loginUrl =
      from && from !== "/login"
        ? `/login?from=${encodeURIComponent(from)}`
        : "/login";
    window.location.href = loginUrl;
  }
}

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    const status = error.response?.status;

    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      shouldAttemptRefresh(originalRequest.url)
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(api(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const tokens = await refreshAccessToken();
        processRefreshQueue(null, tokens.access_token);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        processRefreshQueue(refreshError, null);
        redirectToLogin();
        return Promise.reject(parseApiError(refreshError));
      } finally {
        isRefreshing = false;
      }
    }

    const apiError = parseApiError(error);
    if (status === 401 && shouldAttemptRefresh(originalRequest?.url)) {
      redirectToLogin();
    }
    return Promise.reject(apiError);
  }
);
