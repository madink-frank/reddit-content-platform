import { apiClient } from '../apiClient';
import { ProcessLog, TaskStatus, PaginatedResponse } from '../../types';

export interface TaskListParams {
  page?: number;
  size?: number;
  task_type?: string;
  status?: 'pending' | 'running' | 'completed' | 'failed';
  date_from?: string;
  date_to?: string;
}

export interface CrawlTaskRequest {
  keyword_ids?: number[];
  schedule?: string; // cron expression for scheduling
}

export const tasksApi = {
  // Get task history/logs
  getTasks: async (params?: TaskListParams): Promise<PaginatedResponse<ProcessLog>> => {
    return apiClient.get<PaginatedResponse<ProcessLog>>('/api/v1/tasks', { params });
  },

  // Get task status by ID
  getTaskStatus: async (taskId: string): Promise<TaskStatus> => {
    return apiClient.get<TaskStatus>(`/api/v1/tasks/${taskId}/status`);
  },

  // Start crawling task
  startCrawling: async (data: CrawlTaskRequest): Promise<{ task_id: string }> => {
    return apiClient.post<{ task_id: string }>('/api/v1/tasks/crawl', data);
  },

  // Stop/cancel task
  cancelTask: async (taskId: string): Promise<void> => {
    return apiClient.post<void>(`/api/v1/tasks/${taskId}/cancel`);
  },

  // Get active tasks
  getActiveTasks: async (): Promise<TaskStatus[]> => {
    return apiClient.get<TaskStatus[]>('/api/v1/tasks/active');
  },

  // Get task statistics
  getTaskStats: async (params?: { date_from?: string; date_to?: string }) => {
    return apiClient.get('/api/v1/tasks/stats', { params });
  },

  // Retry failed task
  retryTask: async (taskId: string): Promise<{ task_id: string }> => {
    return apiClient.post<{ task_id: string }>(`/api/v1/tasks/${taskId}/retry`);
  },
};