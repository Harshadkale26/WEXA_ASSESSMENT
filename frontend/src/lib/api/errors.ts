import { AxiosError } from "axios";

import { ApiError } from "@/types/api";

type FastApiDetail =
  | string
  | { msg: string; type?: string; loc?: (string | number)[] }[];

export function parseApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof AxiosError) {
    const status = error.response?.status ?? 500;
    const detail = error.response?.data?.detail as FastApiDetail | undefined;
    const message = formatDetail(detail) ?? error.message ?? "Request failed";
    return new ApiError(message, status);
  }

  if (error instanceof Error) {
    return new ApiError(error.message, 500);
  }

  return new ApiError("An unexpected error occurred", 500);
}

function formatDetail(detail: FastApiDetail | undefined): string | null {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = item.loc?.slice(-1)[0];
        const prefix = field ? `${String(field)}: ` : "";
        return `${prefix}${item.msg}`;
      })
      .join(". ");
  }
  return null;
}
