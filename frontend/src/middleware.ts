import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { AUTH_COOKIE, PUBLIC_ROUTES, ROUTES } from "@/lib/constants";

const PROTECTED_PREFIXES = ["/dashboard", "/analytics", "/dashboards", "/ingestion", "/settings"];

function isProtected(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(AUTH_COOKIE)?.value;

  const isPublic = PUBLIC_ROUTES.includes(pathname as (typeof PUBLIC_ROUTES)[number]);
  const needsAuth = isProtected(pathname);

  if (needsAuth && !token) {
    const login = new URL(ROUTES.login, request.url);
    login.searchParams.set("from", pathname);
    return NextResponse.redirect(login);
  }

  if (isPublic && token) {
    return NextResponse.redirect(new URL(ROUTES.dashboard, request.url));
  }

  if (pathname === ROUTES.home) {
    return NextResponse.redirect(
      new URL(token ? ROUTES.dashboard : ROUTES.login, request.url)
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
