import { apiClient } from '../apiClient';
import { ApiResponse } from '../../types';

export interface CrawlKeywordRequest {
  keyword_id: number;
  limit?: number;
  time_filter?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
  sort?: 'relevance' | 'hot' | 'top' | 'new' | 'comments';
  include_comments?: boolean;
  comment_limit?: number;
}

export interface CrawlAllKeywordsRequest {
  limit_per_keyword?: number;
  time_filter?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
  sort?: 'relevance' | 'hot' | 'top' | 'new' | 'comments';
}

export interface CrawlSubredditRequest {
  subreddit_name: string;
  keyword_id: number;
  limit?: number;
  sort?: 'hot' | 'new' | 'top' | 'rising';
}

export interface CrawlTaskResponse {
  task_id: string;
  status: string;
  message: string;
  keyword_id?: number;
  keyword?: string;
  limit?: number;
  time_filter?: string;
  sort?: string;
  include_comments?: boolean;
  comment_limit?: number;
  process_log_id: number;
}

export interface CrawlStatusResponse {
  tasks: CrawlTaskInfo[];
  total: number;
}

export interface CrawlTaskInfo {
  id: number;
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  completed_at?: string;
  error_message?: string;
  celery_status?: string;
  progress?: number;
  result?: any;
  metadata?: {
    keyword_id?: number;
    keyword?: string;
    limit?: number;
    time_filter?: string;
    sort?: string;
    subreddit?: string;
  };
}

export interface CrawlStatistics {
  period_days: number;
  crawling_tasks: {
    total: number;
    completed: number;
    failed: number;
    running: number;
    pending: number;
    cancelled: number;
    success_rate: number;
  };
  overall_stats: {
    total_tasks: number;
    completed: number;
    failed: number;
    running: number;
    pending: number;
    cancelled: number;
    success_rate: number;
    by_type: Record<string, any>;
  };
}

export const crawlingApi = {
  // Start crawling for a specific keyword
  startKeywordCrawl: async (data: CrawlKeywordRequest): Promise<ApiResponse<CrawlTaskResponse>> => {
    const { keyword_id, ...params } = data;
    return apiClient.post<ApiResponse<CrawlTaskResponse>>(
      `/api/v1/crawling/keyword/${keyword_id}`,
      null,
      { params }
    );
  },

  // Start crawling for all active keywords
  startAllKeywordsCrawl: async (data: CrawlAllKeywordsRequest): Promise<ApiResponse<CrawlTaskResponse>> => {
    return apiClient.post<ApiResponse<CrawlTaskResponse>>(
      '/api/v1/crawling/all-keywords',
      null,
      { params: data }
    );
  },

  // Start crawling for a specific subreddit
  startSubredditCrawl: async (data: CrawlSubredditRequest): Promise<ApiResponse<CrawlTaskResponse>> => {
    const { subreddit_name, keyword_id, ...params } = data;
    return apiClient.post<ApiResponse<CrawlTaskResponse>>(
      '/api/v1/crawling/subreddit',
      null,
      { params: { subreddit_name, keyword_id, ...params } }
    );
  },

  // Get crawling status for all tasks
  getCrawlStatus: async (limit?: number): Promise<ApiResponse<CrawlStatusResponse>> => {
    return apiClient.get<ApiResponse<CrawlStatusResponse>>(
      '/api/v1/crawling/status',
      { params: { limit } }
    );
  },

  // Get crawling statistics
  getCrawlStatistics: async (days?: number): Promise<ApiResponse<CrawlStatistics>> => {
    return apiClient.get<ApiResponse<CrawlStatistics>>(
      '/api/v1/crawling/statistics',
      { params: { days } }
    );
  },

  // Cancel a crawling task
  cancelCrawlTask: async (taskId: string): Promise<ApiResponse<{ task_id: string; status: string; message: string }>> => {
    return apiClient.delete<ApiResponse<{ task_id: string; status: string; message: string }>>(
      `/api/v1/crawling/task/${taskId}`
    );
  },
};