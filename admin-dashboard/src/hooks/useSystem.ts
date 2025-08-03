import { useQuery } from '@tanstack/react-query';
import { systemApi } from '../services/api/systemApi';
import { queryKeys } from '../services/queryClient';

export const useSystemHealth = () => {
  return useQuery({
    queryKey: queryKeys.system.health,
    queryFn: () => systemApi.getHealth(),
    refetchInterval: 30 * 1000, // Poll every 30 seconds
    staleTime: 0, // Always fetch fresh health data
    retry: 1, // Only retry once for health checks
  });
};

export const useSystemHealthDetailed = () => {
  return useQuery({
    queryKey: ['system', 'health', 'detailed'],
    queryFn: () => systemApi.getSystemHealth(),
    refetchInterval: 30 * 1000, // Poll every 30 seconds
    staleTime: 0, // Always fetch fresh health data
    retry: 1, // Only retry once for health checks
  });
};

export const useSystemMetrics = (params?: { time_range?: string }) => {
  return useQuery({
    queryKey: queryKeys.system.metrics(params?.time_range),
    queryFn: () => systemApi.getMetrics(params),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 60 * 1000, // Refetch every minute
  });
};

export const useSystemAlerts = (params?: { resolved?: boolean }) => {
  return useQuery({
    queryKey: ['system', 'alerts', params?.resolved],
    queryFn: () => systemApi.getAlerts(params),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
};

export const useAppInfo = () => {
  return useQuery({
    queryKey: ['system', 'info'],
    queryFn: () => systemApi.getAppInfo(),
    staleTime: 30 * 60 * 1000, // 30 minutes - app info doesn't change often
  });
};