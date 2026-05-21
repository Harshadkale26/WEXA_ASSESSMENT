export const AUTH_COOKIE = "access_token";
export const API_PREFIX = "/api/v1";

export const ROUTES = {
  home: "/",
  login: "/login",
  signup: "/signup",
  dashboard: "/dashboard",
  analytics: "/analytics",
  dashboards: "/dashboards",
  ingestion: "/ingestion",
  settings: "/settings",
} as const;

export const PUBLIC_ROUTES = [ROUTES.login, ROUTES.signup] as const;
