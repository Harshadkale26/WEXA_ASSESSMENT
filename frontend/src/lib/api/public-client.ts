import axios from "axios";

import { API_PREFIX } from "@/lib/constants";
import { config } from "@/lib/config";

/** Axios instance for unauthenticated auth endpoints (no interceptors). */
export const publicApi = axios.create({
  baseURL: `${config.apiUrl}${API_PREFIX}`,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});
