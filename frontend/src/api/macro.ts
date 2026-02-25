import { api } from './client';
import type {
  DashboardData,
  FetchStatus,
  IndicatorHistory,
  IndicatorOut,
  RegimeHistory,
  RegimeOut,
} from '../types/macro';

export async function fetchDashboard(): Promise<DashboardData> {
  const { data } = await api.get('/dashboard');
  return data;
}

export async function fetchIndicators(): Promise<IndicatorOut[]> {
  const { data } = await api.get('/indicators');
  return data;
}

export async function fetchIndicatorHistory(
  seriesId: string,
  start?: string,
  end?: string
): Promise<IndicatorHistory> {
  const params: Record<string, string> = {};
  if (start) params.start = start;
  if (end) params.end = end;
  const { data } = await api.get(`/indicators/${seriesId}/history`, { params });
  return data;
}

export async function fetchCurrentRegime(): Promise<RegimeOut | null> {
  const { data } = await api.get('/regime/current');
  return data;
}

export async function fetchRegimeHistory(limit = 365): Promise<RegimeHistory> {
  const { data } = await api.get('/regime/history', { params: { limit } });
  return data;
}

export async function triggerFetch(): Promise<{ status: string; message: string }> {
  const { data } = await api.post('/fetch/trigger');
  return data;
}

export async function fetchFetchStatus(): Promise<FetchStatus[]> {
  const { data } = await api.get('/fetch/status');
  return data;
}
