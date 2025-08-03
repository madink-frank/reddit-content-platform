import { apiClient } from '../apiClient';
import { Keyword, KeywordCreate, KeywordUpdate } from '../../types';

export interface KeywordListParams {
  page?: number;
  per_page?: number;
  active_only?: boolean;
}

export interface KeywordListResponse {
  keywords: Keyword[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export const keywordsApi = {
  // Get all keywords for current user
  getKeywords: async (params?: KeywordListParams): Promise<KeywordListResponse> => {
    return apiClient.get<KeywordListResponse>('/api/v1/keywords', { params });
  },

  // Get keyword by ID
  getKeyword: async (id: number): Promise<Keyword> => {
    return apiClient.get<Keyword>(`/api/v1/keywords/${id}`);
  },

  // Create new keyword
  createKeyword: async (data: KeywordCreate): Promise<Keyword> => {
    return apiClient.post<Keyword>('/api/v1/keywords', data);
  },

  // Update keyword
  updateKeyword: async (id: number, data: KeywordUpdate): Promise<Keyword> => {
    return apiClient.put<Keyword>(`/api/v1/keywords/${id}`, data);
  },

  // Delete keyword
  deleteKeyword: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/api/v1/keywords/${id}`);
  },

  // Toggle keyword active status
  toggleKeyword: async (id: number): Promise<Keyword> => {
    return apiClient.patch<Keyword>(`/api/v1/keywords/${id}/toggle`);
  },
};