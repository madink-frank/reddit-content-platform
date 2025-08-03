import { QueryClient } from '@tanstack/react-query';
import { useNotificationStore } from '../stores/notificationStore';

// Create a custom query client with enhanced error handling
export const createQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
        retry: (failureCount, error) => {
          // Don't retry on 4xx errors (client errors)
          if (error && typeof error === 'object' && 'response' in error) {
            const status = (error as any).response?.status;
            if (status >= 400 && status < 500) {
              return false;
            }
          }
          // Retry up to 3 times for other errors
          return failureCount < 3;
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
      mutations: {
        retry: false,
        onError: (error) => {
          // Global error handling for mutations
          const { addNotification } = useNotificationStore.getState();
          
          let errorMessage = 'An unexpected error occurred';
          if (error && typeof error === 'object' && 'message' in error) {
            errorMessage = (error as { message: string }).message;
          }
          
          addNotification({
            type: 'error',
            title: 'Operation Failed',
            message: errorMessage,
            duration: 5000,
          });
        },
      },
    },
  });
};

// Query keys factory for consistent key management
export const queryKeys = {
  // Auth
  auth: {
    user: ['auth', 'user'] as const,
    tokens: ['auth', 'tokens'] as const,
  },
  
  // Keywords
  keywords: {
    all: ['keywords'] as const,
    list: (userId?: number) => ['keywords', 'list', userId] as const,
    detail: (id: number) => ['keywords', 'detail', id] as const,
  },
  
  // Posts
  posts: {
    all: ['posts'] as const,
    list: (params?: Record<string, any>) => ['posts', 'list', params] as const,
    detail: (id: number) => ['posts', 'detail', id] as const,
    byKeyword: (keywordId: number, params?: Record<string, any>) => 
      ['posts', 'byKeyword', keywordId, params] as const,
  },
  
  // Trends
  trends: {
    all: ['trends'] as const,
    list: (params?: Record<string, any>) => ['trends', 'list', params] as const,
    detail: (keywordId: number) => ['trends', 'detail', keywordId] as const,
    analytics: (timeRange?: string) => ['trends', 'analytics', timeRange] as const,
  },
  
  // Content
  content: {
    all: ['content'] as const,
    list: (params?: Record<string, any>) => ['content', 'list', params] as const,
    detail: (id: number) => ['content', 'detail', id] as const,
    templates: ['content', 'templates'] as const,
  },
  
  // Tasks
  tasks: {
    all: ['tasks'] as const,
    list: (params?: Record<string, any>) => ['tasks', 'list', params] as const,
    status: (taskId: string) => ['tasks', 'status', taskId] as const,
  },
  
  // System
  system: {
    health: ['system', 'health'] as const,
    healthDetailed: ['system', 'health', 'detailed'] as const,
    metrics: (timeRange?: string) => ['system', 'metrics', timeRange] as const,
    alerts: (resolved?: boolean) => ['system', 'alerts', resolved] as const,
    info: ['system', 'info'] as const,
  },
} as const;