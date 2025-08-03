import { apiClient } from '../apiClient';
import { PostDetail, PostListResponse } from '../../types';

export interface PostListParams {
  page?: number;
  per_page?: number;
  keyword_id?: number;
  subreddit?: string;
  author?: string;
  search?: string;
  sort_by?: 'created_at' | 'post_created_at' | 'score' | 'num_comments' | 'title' | 'author' | 'subreddit';
  sort_order?: 'asc' | 'desc';
  min_score?: number;
  max_score?: number;
  date_from?: string;
  date_to?: string;
}

export const postsApi = {
  // Get paginated list of posts
  getPosts: async (params?: PostListParams): Promise<PostListResponse> => {
    return apiClient.get<PostListResponse>('/api/v1/posts', { params });
  },

  // Get post by ID with comments
  getPost: async (id: number): Promise<PostDetail> => {
    return apiClient.get<PostDetail>(`/api/v1/posts/${id}`);
  },

  // Get posts by keyword
  getPostsByKeyword: async (
    keywordId: number,
    params?: Omit<PostListParams, 'keyword_id'>
  ): Promise<PostListResponse> => {
    return apiClient.get<PostListResponse>(`/api/v1/posts/keyword/${keywordId}`, {
      params,
    });
  },

  // Search posts
  searchPosts: async (query: string, params?: Omit<PostListParams, 'search'>): Promise<PostListResponse> => {
    return apiClient.get<PostListResponse>('/api/v1/posts/search/query', {
      params: { ...params, q: query },
    });
  },

  // Get post statistics
  getPostStats: async (params?: { keyword_id?: number; date_from?: string; date_to?: string }) => {
    return apiClient.get('/api/v1/posts/stats/summary', { params });
  },
};