export interface IndicatorOut {
  id: number;
  series_id: string;
  name: string;
  category: string;
  source: string;
  frequency: string;
  weight: number;
  higher_is_bullish: boolean;
  unit: string;
  description: string;
  latest_value: number | null;
  latest_date: string | null;
  z_score: number | null;
  percentile: number | null;
  change_1d: number | null;
  change_1w: number | null;
  change_1m: number | null;
  signal: 'bullish' | 'bearish' | 'neutral' | null;
  sparkline: number[];
}

export interface RegimeOut {
  date: string;
  regime: 'goldilocks' | 'reflation' | 'deflation' | 'stagflation';
  growth_score: number;
  inflation_score: number;
  confidence: number;
  composite_score: number;
  component_scores: Record<string, unknown>;
}

export interface CategorySummary {
  name: string;
  signal: 'bullish' | 'bearish' | 'neutral';
  score: number;
  key_indicators: IndicatorOut[];
}

export interface DashboardData {
  last_updated: string | null;
  regime: RegimeOut | null;
  composite_score: number;
  categories: CategorySummary[];
  indicators: IndicatorOut[];
}

export interface RegimeHistory {
  snapshots: RegimeOut[];
}

export interface IndicatorHistory {
  series_id: string;
  name: string;
  category: string;
  values: { date: string; value: number; z_score: number | null; percentile: number | null }[];
}

export interface FetchStatus {
  source: string;
  last_fetch: string | null;
  status: string | null;
  records_added: number;
  error_message: string | null;
}
