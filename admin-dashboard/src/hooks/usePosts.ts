import { useQuery } from '@tanstack/react-query';
import { postsApi, PostListParams } from '../services/api/postsApi';
import { queryKeys } from '../services/queryClient';

export const usePosts = (params?: PostListParams) => {
  return useQuery({
    queryKey: queryKeys.posts.list(params),
    queryFn: () => postsApi.getPosts(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const usePost = (id: number) => {
  return useQuery({
    queryKey: queryKeys.posts.detail(id),
    queryFn: () => postsApi.getPost(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const usePostsByKeyword = (keywordId: number, params?: Omit<PostListParams, 'keyword_id'>) => {
  return useQuery({
    queryKey: queryKeys.posts.byKeyword(keywordId, params),
    queryFn: () => postsApi.getPostsByKeyword(keywordId, params),
    enabled: !!keywordId,
    staleTime: 5 * 60 * 1000,
  });
};

export const useSearchPosts = (query: string, params?: Omit<PostListParams, 'search'>) => {
  return useQuery({
    queryKey: ['posts', 'search', query, params],
    queryFn: () => postsApi.searchPosts(query, params),
    enabled: !!query && query.length > 2,
    staleTime: 2 * 60 * 1000,
  });
};

export const usePostStats = (params?: { keyword_id?: number; date_from?: string; date_to?: string }) => {
  return useQuery({
    queryKey: ['posts', 'stats', params],
    queryFn: () => postsApi.getPostStats(params),
    staleTime: 10 * 60 * 1000,
  });
};