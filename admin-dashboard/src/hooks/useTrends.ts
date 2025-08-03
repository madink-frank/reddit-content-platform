import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { trendsApi, TrendAnalysisParams } from '../services/api/trendsApi';
import { queryKeys } from '../services/queryClient';
import { useNotificationStore } from '../stores/notificationStore';

export const useTrends = (params?: TrendAnalysisParams) => {
  return useQuery({
    queryKey: queryKeys.trends.list(params),
    queryFn: () => trendsApi.getTrends(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useKeywordTrend = (keywordId: number, params?: Omit<TrendAnalysisParams, 'keyword_id'>) => {
  return useQuery({
    queryKey: queryKeys.trends.detail(keywordId),
    queryFn: () => trendsApi.getKeywordTrend(keywordId, params),
    enabled: !!keywordId,
    staleTime: 5 * 60 * 1000,
  });
};

export const useTrendingTopics = (params?: { limit?: number; time_range?: string }) => {
  return useQuery({
    queryKey: ['trends', 'topics', params],
    queryFn: () => trendsApi.getTrendingTopics(params),
    staleTime: 10 * 60 * 1000,
  });
};

export const useTrendHistory = (keywordId: number, params?: { date_from?: string; date_to?: string }) => {
  return useQuery({
    queryKey: ['trends', 'history', keywordId, params],
    queryFn: () => trendsApi.getTrendHistory(keywordId, params),
    enabled: !!keywordId,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

export const useAnalyzeTrends = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (keywordIds?: number[]) => trendsApi.analyzeTrends(keywordIds),
    onSuccess: (result) => {
      // Invalidate trends queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.trends.all });
      
      addNotification({
        type: 'success',
        title: 'Trend Analysis Started',
        message: `Analysis task ${result.task_id} has been started. Results will be available shortly.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Start Trend Analysis',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};