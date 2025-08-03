import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  crawlingApi, 
  CrawlKeywordRequest, 
  CrawlAllKeywordsRequest, 
  CrawlSubredditRequest 
} from '../services/api/crawlingApi';
import { useNotificationStore } from '../stores/notificationStore';

// Query keys for crawling-related queries
export const crawlingQueryKeys = {
  all: ['crawling'] as const,
  status: () => [...crawlingQueryKeys.all, 'status'] as const,
  statistics: (days?: number) => [...crawlingQueryKeys.all, 'statistics', days] as const,
};

// Hook to get crawling status
export const useCrawlStatus = (limit?: number) => {
  return useQuery({
    queryKey: [...crawlingQueryKeys.status(), limit],
    queryFn: () => crawlingApi.getCrawlStatus(limit),
    refetchInterval: 3000, // Poll every 3 seconds for real-time updates
    staleTime: 0, // Always fetch fresh data
  });
};

// Hook to get crawling statistics
export const useCrawlStatistics = (days: number = 7) => {
  return useQuery({
    queryKey: crawlingQueryKeys.statistics(days),
    queryFn: () => crawlingApi.getCrawlStatistics(days),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook to start keyword crawling
export const useStartKeywordCrawl = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: CrawlKeywordRequest) => crawlingApi.startKeywordCrawl(data),
    onSuccess: (response) => {
      const { data } = response;
      queryClient.invalidateQueries({ queryKey: crawlingQueryKeys.status() });
      
      addNotification({
        type: 'success',
        title: 'Crawling Started',
        message: `Started crawling for keyword "${data.keyword}" (Task ID: ${data.task_id})`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Start Crawling',
        message: error.response?.data?.message || error.message || 'An unexpected error occurred.',
      });
    },
  });
};

// Hook to start crawling all keywords
export const useStartAllKeywordsCrawl = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: CrawlAllKeywordsRequest) => crawlingApi.startAllKeywordsCrawl(data),
    onSuccess: (response) => {
      const { data } = response;
      queryClient.invalidateQueries({ queryKey: crawlingQueryKeys.status() });
      
      addNotification({
        type: 'success',
        title: 'Bulk Crawling Started',
        message: `Started crawling for all active keywords (Task ID: ${data.task_id})`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Start Bulk Crawling',
        message: error.response?.data?.message || error.message || 'An unexpected error occurred.',
      });
    },
  });
};

// Hook to start subreddit crawling
export const useStartSubredditCrawl = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: CrawlSubredditRequest) => crawlingApi.startSubredditCrawl(data),
    onSuccess: (response) => {
      const { data } = response;
      queryClient.invalidateQueries({ queryKey: crawlingQueryKeys.status() });
      
      addNotification({
        type: 'success',
        title: 'Subreddit Crawling Started',
        message: `Started crawling subreddit (Task ID: ${data.task_id})`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Start Subreddit Crawling',
        message: error.response?.data?.message || error.message || 'An unexpected error occurred.',
      });
    },
  });
};

// Hook to cancel crawling task
export const useCancelCrawlTask = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (taskId: string) => crawlingApi.cancelCrawlTask(taskId),
    onSuccess: (_, taskId) => {
      queryClient.invalidateQueries({ queryKey: crawlingQueryKeys.status() });
      
      addNotification({
        type: 'success',
        title: 'Task Cancelled',
        message: `Crawling task ${taskId} has been cancelled.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Cancel Task',
        message: error.response?.data?.message || error.message || 'An unexpected error occurred.',
      });
    },
  });
};