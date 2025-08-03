import { apiClient } from '../apiClient';
import { TrendData, TrendMetrics } from '../../types';

export interface TrendAnalysisParams {
  keyword_id?: number;
  time_range?: '1h' | '6h' | '24h' | '7d' | '30d';
  limit?: number;
}

export interface TrendAnalyticsResponse {
  trends: TrendData[];
  summary: {
    total_keywords: number;
    trending_up: number;
    trending_down: number;
    stable: number;
  };
  top_keywords: Array<{
    keyword: string;
    engagement_score: number;
    trend_velocity: number;
  }>;
}

export const trendsApi = {
  // Get trend analysis for keywords
  getTrends: async (params?: TrendAnalysisParams): Promise<TrendAnalyticsResponse> => {
    return apiClient.get<TrendAnalyticsResponse>('/api/v1/trends', { params });
  },

  // Get trend data for specific keyword
  getKeywordTrend: async (keywordId: number, params?: Omit<TrendAnalysisParams, 'keyword_id'>): Promise<TrendData> => {
    return apiClient.get<TrendData>(`/api/v1/trends/keywords/${keywordId}`, { params });
  },

  // Trigger trend analysis
  analyzeTrends: async (keywordIds?: number[]): Promise<{ task_id: string }> => {
    return apiClient.post<{ task_id: string }>('/api/v1/trends/analyze', {
      keyword_ids: keywordIds,
    });
  },

  // Get trending topics
  getTrendingTopics: async (params?: { limit?: number; time_range?: string }) => {
    return apiClient.get('/api/v1/trends/topics', { params });
  },

  // Get trend metrics history
  getTrendHistory: async (
    keywordId: number,
    params?: { date_from?: string; date_to?: string }
  ): Promise<TrendMetrics[]> => {
    return apiClient.get<TrendMetrics[]>(`/api/v1/trends/keywords/${keywordId}/history`, {
      params,
    });
  },
};