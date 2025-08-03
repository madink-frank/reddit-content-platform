import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { keywordsApi, KeywordListParams } from '../services/api/keywordsApi';
import { queryKeys } from '../services/queryClient';
import { useNotificationStore } from '../stores/notificationStore';
import { Keyword, KeywordCreate, KeywordUpdate } from '../types';

// Query hooks
export const useKeywords = (params?: KeywordListParams) => {
  return useQuery({
    queryKey: queryKeys.keywords.list(params?.page),
    queryFn: () => keywordsApi.getKeywords(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    select: (data) => ({
      ...data,
      items: data.keywords, // Map keywords to items for compatibility
    }),
  });
};

export const useKeyword = (id: number) => {
  return useQuery({
    queryKey: queryKeys.keywords.detail(id),
    queryFn: () => keywordsApi.getKeyword(id),
    enabled: !!id,
  });
};

// Mutation hooks
export const useCreateKeyword = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: KeywordCreate) => keywordsApi.createKeyword(data),
    onSuccess: (newKeyword: Keyword) => {
      // Invalidate and refetch keywords list
      queryClient.invalidateQueries({ queryKey: queryKeys.keywords.all });
      
      addNotification({
        type: 'success',
        title: 'Keyword Created',
        message: `Keyword "${newKeyword.keyword}" has been created successfully.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Create Keyword',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useUpdateKeyword = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: KeywordUpdate }) =>
      keywordsApi.updateKeyword(id, data),
    onSuccess: (updatedKeyword: Keyword) => {
      // Update the specific keyword in cache
      queryClient.setQueryData(
        queryKeys.keywords.detail(updatedKeyword.id),
        updatedKeyword
      );
      
      // Invalidate keywords list to reflect changes
      queryClient.invalidateQueries({ queryKey: queryKeys.keywords.all });
      
      addNotification({
        type: 'success',
        title: 'Keyword Updated',
        message: `Keyword "${updatedKeyword.keyword}" has been updated successfully.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Update Keyword',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useDeleteKeyword = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (id: number) => keywordsApi.deleteKeyword(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: queryKeys.keywords.detail(deletedId) });
      
      // Invalidate keywords list
      queryClient.invalidateQueries({ queryKey: queryKeys.keywords.all });
      
      addNotification({
        type: 'success',
        title: 'Keyword Deleted',
        message: 'Keyword has been deleted successfully.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Delete Keyword',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useToggleKeyword = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (id: number) => keywordsApi.toggleKeyword(id),
    onSuccess: (updatedKeyword: Keyword) => {
      // Update the specific keyword in cache
      queryClient.setQueryData(
        queryKeys.keywords.detail(updatedKeyword.id),
        updatedKeyword
      );
      
      // Invalidate keywords list to reflect changes
      queryClient.invalidateQueries({ queryKey: queryKeys.keywords.all });
      
      const status = updatedKeyword.is_active ? 'activated' : 'deactivated';
      addNotification({
        type: 'success',
        title: 'Keyword Status Updated',
        message: `Keyword "${updatedKeyword.keyword}" has been ${status}.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Toggle Keyword',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};