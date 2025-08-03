import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { contentApi, ContentListParams, ContentUpdateData } from '../services/api/contentApi';
import { queryKeys } from '../services/queryClient';
import { useNotificationStore } from '../stores/notificationStore';
import { ContentGenerationRequest, BlogContent } from '../types';

export const useContent = (params?: ContentListParams) => {
  return useQuery({
    queryKey: queryKeys.content.list(params),
    queryFn: () => contentApi.getContent(params),
    staleTime: 5 * 60 * 1000,
  });
};

export const useContentById = (id: number) => {
  return useQuery({
    queryKey: queryKeys.content.detail(id),
    queryFn: () => contentApi.getContentById(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  });
};

export const useContentTemplates = () => {
  return useQuery({
    queryKey: queryKeys.content.templates,
    queryFn: () => contentApi.getTemplates(),
    staleTime: 30 * 60 * 1000, // 30 minutes - templates don't change often
    select: (data) => data.templates,
  });
};

export const useGenerateContent = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: ContentGenerationRequest) => contentApi.generateContent(data),
    onSuccess: (result) => {
      // Invalidate content queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.content.all });
      
      addNotification({
        type: 'success',
        title: 'Content Generation Started',
        message: `Generation task ${result.task_id} has been started. Content will be available shortly.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Generate Content',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const usePreviewContent = () => {
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (data: ContentGenerationRequest) => contentApi.previewContent(data),
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Generate Preview',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useGenerationStatus = (taskId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['content', 'generation-status', taskId],
    queryFn: () => contentApi.getGenerationStatus(taskId),
    enabled: enabled && !!taskId,
    refetchInterval: (query) => {
      // Stop polling when task is completed or failed
      if (query.state.data?.status === 'completed' || query.state.data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
    staleTime: 0, // Always fetch fresh data
  });
};

export const useUpdateContent = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ContentUpdateData }) =>
      contentApi.updateContent(id, data),
    onSuccess: (updatedContent: BlogContent) => {
      // Update the specific content in cache
      queryClient.setQueryData(
        queryKeys.content.detail(updatedContent.id),
        updatedContent
      );
      
      // Invalidate content list to reflect changes
      queryClient.invalidateQueries({ queryKey: queryKeys.content.all });
      
      addNotification({
        type: 'success',
        title: 'Content Updated',
        message: 'Content has been updated successfully.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Update Content',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useDeleteContent = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (id: number) => contentApi.deleteContent(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: queryKeys.content.detail(deletedId) });
      
      // Invalidate content list
      queryClient.invalidateQueries({ queryKey: queryKeys.content.all });
      
      addNotification({
        type: 'success',
        title: 'Content Deleted',
        message: 'Content has been deleted successfully.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Delete Content',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useRegenerateContent = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ id, templateType, customPrompt }: { 
      id: number; 
      templateType?: string; 
      customPrompt?: string; 
    }) => contentApi.regenerateContent(id, templateType, customPrompt),
    onSuccess: (result) => {
      // Invalidate content queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.content.all });
      
      addNotification({
        type: 'success',
        title: 'Content Regeneration Started',
        message: `Regeneration task ${result.task_id} has been started.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Regenerate Content',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};

export const useBatchGenerateContent = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ keywordIds, options }: { 
      keywordIds: number[]; 
      options: Partial<ContentGenerationRequest>; 
    }) => contentApi.batchGenerateContent(keywordIds, options),
    onSuccess: (result) => {
      // Invalidate content queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.content.all });
      
      addNotification({
        type: 'success',
        title: 'Batch Generation Started',
        message: `Batch generation task ${result.task_id} has been started.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Failed to Start Batch Generation',
        message: error.message || 'An unexpected error occurred.',
      });
    },
  });
};