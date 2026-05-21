import { api } from "@/lib/api/client";
import type {
  Dashboard,
  DashboardDetail,
  Widget,
  WidgetDataQueryOverride,
  WidgetDataResponse,
} from "@/types/dashboard";

export const dashboardsApi = {
  list: () => api.get<Dashboard[]>("/dashboards").then((r) => r.data),

  get: (dashboardId: string) =>
    api.get<DashboardDetail>(`/dashboards/${dashboardId}`).then((r) => r.data),

  listWidgets: (dashboardId: string) =>
    api.get<Widget[]>(`/dashboards/${dashboardId}/widgets`).then((r) => r.data),

  bootstrap: () =>
    api.post<DashboardDetail>("/dashboards/bootstrap").then((r) => r.data),
};

export const widgetsApi = {
  getData: (widgetId: string, override?: WidgetDataQueryOverride) =>
    api
      .post<WidgetDataResponse>(`/widgets/${widgetId}/data`, override ?? {})
      .then((r) => r.data),
};
