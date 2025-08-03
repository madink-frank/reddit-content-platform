import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { tasksApi, TaskListParams, CrawlTaskRequest } from '../services/api/tasksApi';
import { queryKeys } from '../services/queryClient';
import { useNotificationStore } from '../stores/notificationStore';

export const useTasks = (params?: TaskListParams) => {
  return useQuery({
    queryKey: queryKeys.tasks.list(params),
    queryFn: () => tasksApi.getTasks(params),
    staleTime: 30 * 1000, // 30 seconds - tasks change frequently
  });
};

export const useTaskStatus = (taskId: string) => {
  return useQuery({
    queryKey: queryKeys.tasks.status(taskId),
    queryFn: () => tasksApi.getTaskStatus(taskId),
    enabled: !!taskId,
    refetchInterval: (query) => {
      // Poll every 2 seconds if task is running, otherwise stop polling
      const data = query.state.data;
      return data?.status === 'running' || data?.status === 'pending' ? 2000 : false;
    },
    staleTime: 0, // Always fetch fresh data for task status
  });
};

export const useActiveTasks = () => {
  return useQuery({
    queryKey: ['tasks', 'active'],
    queryFn: () => tasksApi.getActiveTasks(),
    refetchInterval: 5000, // Poll every 5 seconds
    staleTime: 0,
  });
};

export const useTaskStats = (params?: { date_from?: string; date_to?: string }) => {
  return useQuery({
    queryKey: ['tasks', 'stats', params],
    queryFn: () => tasksApi.getTaskStats(params),
    staleTime: 5 * 60 * 1000,
  });
};

export const useStartCrawling = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: CrawlTaskRequest) => tasksApi.startCrawling(data),
    onSuccess: (result) => {
      // Invalidate tasks queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      
      addNotification({
        type: 'success',
        title: 'Crawling Started',
        message: `Crawling task ${result.task_id} has been started.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Start Crawling',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useCancelTask = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (taskId: string) => tasksApi.cancelTask(taskId),
    onSuccess: (_, taskId) => {
      // Invalidate task status and tasks list
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.status(taskId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      
      addNotification({
        type: 'success',
        title: 'Task Cancelled',
        message: `Task ${taskId} has been cancelled.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Cancel Task',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useRetryTask = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (taskId: string) => tasksApi.retryTask(taskId),
    onSuccess: (result, _) => {
      // Invalidate tasks queries
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      
      addNotification({
        type: 'success',
        title: 'Task Retried',
        message: `Task has been retried with new ID: ${result.task_id}`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Retry Task',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};