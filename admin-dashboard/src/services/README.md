# API Client and State Management

This document explains how to use the implemented API client and state management system in the admin dashboard.

## Overview

The system consists of:
- **Axios-based API Client** with automatic token management and error handling
- **TanStack Query** for server state management
- **Zustand stores** for client-side state management
- **Custom hooks** for each API service

## API Client

### Basic Usage

```typescript
import { apiClient } from '../services/apiClient';

// Basic HTTP methods
const data = await apiClient.get('/api/v1/keywords');
const result = await apiClient.post('/api/v1/keywords', { keyword: 'react' });
```

### Loading State Management

```typescript
// Methods with automatic loading state management
const data = await apiClient.getWithLoading('/api/v1/keywords', 'keywords-loading');
const result = await apiClient.postWithLoading('/api/v1/keywords', data, 'create-keyword');
```

### Features

- **Automatic Token Management**: Adds JWT tokens to requests automatically
- **Token Refresh**: Automatically refreshes expired tokens
- **Error Handling**: Standardized error responses
- **Loading States**: Automatic loading state management via Zustand
- **Request Interceptors**: Adds request IDs and handles authentication

## TanStack Query Integration

### Query Keys

Centralized query key management for cache invalidation:

```typescript
import { queryKeys } from '../services/queryClient';

// Use predefined query keys
const keywordsQuery = useQuery({
  queryKey: queryKeys.keywords.list(),
  queryFn: () => keywordsApi.getKeywords(),
});
```

### Custom Hooks

Each API service has corresponding hooks:

```typescript
// Keywords
import { useKeywords, useCreateKeyword } from '../hooks/useKeywords';

const KeywordsComponent = () => {
  const { data: keywords, isLoading } = useKeywords();
  const createKeyword = useCreateKeyword();

  const handleCreate = (keyword: string) => {
    createKeyword.mutate({ keyword });
  };
};
```

## Zustand Stores

### App Store

Global application state:

```typescript
import { useAppStore } from '../stores';

const Component = () => {
  const { isOnline, features, toggleFeature } = useAppStore();
  
  return (
    <div>
      <p>Online: {isOnline ? 'Yes' : 'No'}</p>
      <button onClick={() => toggleFeature('analytics')}>
        Toggle Analytics: {features.analytics ? 'On' : 'Off'}
      </button>
    </div>
  );
};
```

### UI Store

UI state management:

```typescript
import { useUIStore } from '../stores';

const Layout = () => {
  const { sidebarCollapsed, toggleSidebar, setLoading } = useUIStore();
  
  return (
    <div className={sidebarCollapsed ? 'collapsed' : 'expanded'}>
      <button onClick={toggleSidebar}>Toggle Sidebar</button>
    </div>
  );
};
```

### Notification Store

Toast notifications:

```typescript
import { useNotificationStore } from '../stores';

const Component = () => {
  const { addNotification } = useNotificationStore();
  
  const showSuccess = () => {
    addNotification({
      type: 'success',
      title: 'Success!',
      message: 'Operation completed successfully',
      duration: 5000,
    });
  };
};
```

## API Service Hooks

### Keywords

```typescript
import { 
  useKeywords, 
  useCreateKeyword, 
  useUpdateKeyword, 
  useDeleteKeyword 
} from '../hooks/useKeywords';

const KeywordsPage = () => {
  const { data: keywords, isLoading } = useKeywords();
  const createKeyword = useCreateKeyword();
  const updateKeyword = useUpdateKeyword();
  const deleteKeyword = useDeleteKeyword();

  // Automatic cache invalidation and notifications
  const handleCreate = (keyword: string) => {
    createKeyword.mutate({ keyword });
  };
};
```

### Posts

```typescript
import { usePosts, usePost, usePostsByKeyword } from '../hooks/usePosts';

const PostsPage = () => {
  const { data: posts } = usePosts({ page: 1, size: 20 });
  const { data: post } = usePost(123);
  const { data: keywordPosts } = usePostsByKeyword(456);
};
```

### Trends

```typescript
import { useTrends, useAnalyzeTrends } from '../hooks/useTrends';

const TrendsPage = () => {
  const { data: trends } = useTrends({ time_range: '24h' });
  const analyzeTrends = useAnalyzeTrends();

  const handleAnalyze = () => {
    analyzeTrends.mutate([1, 2, 3]); // keyword IDs
  };
};
```

### Content

```typescript
import { 
  useContent, 
  useGenerateContent, 
  useContentTemplates 
} from '../hooks/useContent';

const ContentPage = () => {
  const { data: content } = useContent();
  const { data: templates } = useContentTemplates();
  const generateContent = useGenerateContent();

  const handleGenerate = (keywordId: number, templateId: string) => {
    generateContent.mutate({ keyword_id: keywordId, template_id: templateId });
  };
};
```

### Tasks

```typescript
import { 
  useTasks, 
  useTaskStatus, 
  useStartCrawling, 
  useActiveTasks 
} from '../hooks/useTasks';

const TasksPage = () => {
  const { data: tasks } = useTasks();
  const { data: activeTasks } = useActiveTasks(); // Auto-polling
  const startCrawling = useStartCrawling();

  const handleStartCrawling = (keywordIds: number[]) => {
    startCrawling.mutate({ keyword_ids: keywordIds });
  };
};
```

### System Health

```typescript
import { useSystemHealth, useSystemMetrics } from '../hooks/useSystem';

const HealthPage = () => {
  const { data: health } = useSystemHealth(); // Auto-polling every 30s
  const { data: metrics } = useSystemMetrics({ time_range: '1h' });

  return (
    <div>
      <p>Status: {health?.status}</p>
      <p>Database: {health?.services.database ? 'OK' : 'Error'}</p>
    </div>
  );
};
```

## Loading State Management

### Using the Loading Hook

```typescript
import { useLoadingState } from '../hooks/useLoadingState';

const Component = () => {
  const { isLoading, setLoading } = useLoadingState('my-operation');

  const handleOperation = async () => {
    setLoading(true);
    try {
      await someAsyncOperation();
    } finally {
      setLoading(false);
    }
  };

  return (
    <button disabled={isLoading} onClick={handleOperation}>
      {isLoading ? 'Loading...' : 'Start Operation'}
    </button>
  );
};
```

### Multiple Loading States

```typescript
import { useLoadingStates } from '../hooks/useLoadingState';

const Component = () => {
  const { isLoading, isAnyLoading } = useLoadingStates([
    'operation-1',
    'operation-2',
    'operation-3'
  ]);

  return (
    <div>
      <p>Operation 1: {isLoading('operation-1') ? 'Loading' : 'Ready'}</p>
      <p>Any loading: {isAnyLoading ? 'Yes' : 'No'}</p>
    </div>
  );
};
```

## Error Handling

### Automatic Error Notifications

Mutations automatically show error notifications:

```typescript
const createKeyword = useCreateKeyword();

// This will automatically show an error notification if it fails
createKeyword.mutate({ keyword: 'test' });
```

### Custom Error Handling

```typescript
const createKeyword = useCreateKeyword();

createKeyword.mutate(
  { keyword: 'test' },
  {
    onError: (error) => {
      // Custom error handling
      console.error('Custom error handling:', error);
    },
  }
);
```

## Best Practices

1. **Use Query Keys**: Always use the predefined query keys for consistency
2. **Loading States**: Use the loading state hooks for better UX
3. **Error Handling**: Let mutations handle errors automatically, add custom handling only when needed
4. **Cache Management**: TanStack Query handles cache invalidation automatically
5. **Notifications**: Use the notification store for user feedback
6. **Polling**: Use refetchInterval for real-time data (health checks, active tasks)

## Configuration

### Query Client Configuration

The query client is configured with:
- 5-minute stale time for most queries
- Automatic retry logic (skip 4xx errors)
- Exponential backoff for retries
- Global error handling for mutations

### Store Persistence

- App Store: Persists feature flags
- UI Store: Persists theme and sidebar state
- Notification Store: No persistence (session-only)

## Testing

All stores and API functions are fully tested. See:
- `src/test/stores.test.ts` - Store functionality
- `src/test/apiClient.test.ts` - API client and query keys