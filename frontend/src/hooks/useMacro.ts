import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchDashboard,
  fetchIndicators,
  fetchIndicatorHistory,
  fetchRegimeHistory,
  triggerFetch,
  fetchFetchStatus,
} from '../api/macro';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
}

export function useIndicators() {
  return useQuery({
    queryKey: ['indicators'],
    queryFn: fetchIndicators,
  });
}

export function useIndicatorHistory(seriesId: string | null) {
  return useQuery({
    queryKey: ['indicatorHistory', seriesId],
    queryFn: () => fetchIndicatorHistory(seriesId!),
    enabled: !!seriesId,
  });
}

export function useRegimeHistory(limit = 365) {
  return useQuery({
    queryKey: ['regimeHistory', limit],
    queryFn: () => fetchRegimeHistory(limit),
  });
}

export function useFetchStatus() {
  return useQuery({
    queryKey: ['fetchStatus'],
    queryFn: fetchFetchStatus,
  });
}

export function useTriggerFetch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: triggerFetch,
    onSuccess: () => {
      // Refetch everything after a manual trigger
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        queryClient.invalidateQueries({ queryKey: ['indicators'] });
        queryClient.invalidateQueries({ queryKey: ['fetchStatus'] });
      }, 5000);
    },
  });
}
