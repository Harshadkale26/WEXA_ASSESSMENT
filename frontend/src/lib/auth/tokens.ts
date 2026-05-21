import Cookies from "js-cookie";

import { AUTH_COOKIE } from "@/lib/constants";

const COOKIE_OPTIONS: Cookies.CookieAttributes = {
  sameSite: "lax",
  secure: process.env.NODE_ENV === "production",
  path: "/",
};

export function setAccessTokenCookie(token: string, expiresInSeconds?: number) {
  const expires = expiresInSeconds
    ? new Date(Date.now() + expiresInSeconds * 1000)
    : 7;
  Cookies.set(AUTH_COOKIE, token, { ...COOKIE_OPTIONS, expires });
}

export function getAccessTokenCookie(): string | undefined {
  return Cookies.get(AUTH_COOKIE);
}

export function clearAccessTokenCookie() {
  Cookies.remove(AUTH_COOKIE, { path: "/" });
}

export function computeExpiresAt(expiresInSeconds: number): number {
  return Date.now() + expiresInSeconds * 1000;
}

export function isTokenExpiringSoon(expiresAt: number | null, bufferMs = 60_000): boolean {
  if (!expiresAt) return false;
  return Date.now() >= expiresAt - bufferMs;
}
