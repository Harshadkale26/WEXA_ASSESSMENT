export type WidgetType = "line_chart" | "bar_chart" | "kpi_card" | "pie_chart";

export type AggregationType = "count" | "sum" | "average";

export type TimeRangePreset = "1h" | "24h" | "7d" | "30d" | "custom";

export interface TimeRangeConfig {
  preset?: TimeRangePreset | null;
  start?: string | null;
  end?: string | null;
}

export interface WidgetFilter {
  field: string;
  operator: string;
  value: string | number | boolean | string[] | number[];
}

export interface WidgetQueryConfig {
  metric: string;
  aggregation: AggregationType;
  group_by?: string | null;
  time_bucket?: "hour" | "day" | "week" | "month" | null;
  time_range?: TimeRangeConfig;
  filters?: WidgetFilter[];
}

export interface WidgetLayout {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Dashboard {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  is_default: boolean;
  created_by_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Widget {
  id: string;
  organization_id: string;
  dashboard_id: string;
  title: string;
  widget_type: WidgetType;
  query_config: WidgetQueryConfig;
  layout: WidgetLayout | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface DashboardDetail extends Dashboard {
  widgets: Widget[];
}

export interface WidgetDataPoint {
  label: string;
  value: number;
}

export interface WidgetDataSeries {
  name: string;
  points: WidgetDataPoint[];
}

export interface WidgetDataResponse {
  widget_id: string;
  widget_type: WidgetType;
  aggregation: AggregationType;
  metric: string;
  time_range: { start: string; end: string };
  value?: number | null;
  labels: string[];
  series: WidgetDataSeries[];
  points: WidgetDataPoint[];
  meta: Record<string, unknown>;
}

export interface WidgetDataQueryOverride {
  time_range?: TimeRangeConfig;
  filters?: WidgetFilter[];
}
