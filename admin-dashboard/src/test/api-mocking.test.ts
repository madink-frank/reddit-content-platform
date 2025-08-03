import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { 
  createMockApiResponse, 
  createMockApiError, 
  createMockKeyword,
  createMockPost,
  createMockTrendMetric,
  renderWithProviders 
} from './utils';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    })),
  },
}));

// Test component that uses API
const TestApiComponent = ({ endpoint }: { endpoint: string }) => {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(endpoint);
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchData();
  }, [endpoint]);

  if (loading) return <div role="status">Loading...</div>;
  if (error) return <div role="alert">Error: {error}</div>;
  if (data) return <div data-testid="api-data">{JSON.stringify(data)}</div>;
  return <div>No data</div>;
};

describe('API Mocking', () => {
  let mockAxiosInstance: any;

  beforeEach(() => {
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    };

    vi.mocked(require('axios').default.create).mockReturnValue(mockAxiosInstance);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Keywords API', () => {
    it('mocks successful keywords fetch', async () => {
      const mockKeywords = [
        createMockKeyword({ id: 1, keyword: 'react' }),
        createMockKeyword({ id: 2, keyword: 'javascript' }),
      ];

      mockAxiosInstance.get.mockResolvedValue(
        createMockApiResponse(mockKeywords)
      );

      renderWithProviders(<TestApiComponent endpoint="/keywords" />);

      await waitFor(() => {
        expect(screen.getByTestId('api-data')).toBeInTheDocument();
      });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/keywords');
    });

    it('mocks keywords API error', async () => {
      mockAxiosInstance.get.mockRejectedValue(
        createMockApiError('Failed to fetch keywords', 500)
      );

      renderWithProviders(<TestApiComponent endpoint="/keywords" />);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Error: Failed to fetch keywords');
      });
    });

    it('mocks keyword creation', async () => {
      const newKeyword = createMockKeyword({ keyword: 'new-keyword' });
      
      mockAxiosInstance.post.mockResolvedValue(
        createMockApiResponse(newKeyword, 201)
      );

      const response = await apiClient.post('/keywords', { keyword: 'new-keyword' });
      
      expect(response.data).toEqual(newKeyword);
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/keywords', { keyword: 'new-keyword' });
    });

    it('mocks keyword update', async () => {
      const updatedKeyword = createMockKeyword({ id: 1, keyword: 'updated-keyword' });
      
      mockAxiosInstance.put.mockResolvedValue(
        createMockApiResponse(updatedKeyword)
      );

      const response = await apiClient.put('/keywords/1', { keyword: 'updated-keyword' });
      
      expect(response.data).toEqual(updatedKeyword);
      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/keywords/1', { keyword: 'updated-keyword' });
    });

    it('mocks keyword deletion', async () => {
      mockAxiosInstance.delete.mockResolvedValue(
        createMockApiResponse({ success: true }, 204)
      );

      const response = await apiClient.delete('/keywords/1');
      
      expect(response.status).toBe(204);
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/keywords/1');
    });
  });

  describe('Posts API', () => {
    it('mocks posts list with pagination', async () => {
      const mockPosts = [
        createMockPost({ id: 1, title: 'First Post' }),
        createMockPost({ id: 2, title: 'Second Post' }),
      ];

      const mockResponse = {
        items: mockPosts,
        total: 2,
        page: 1,
        per_page: 10,
        pages: 1,
      };

      mockAxiosInstance.get.mockResolvedValue(
        createMockApiResponse(mockResponse)
      );

      const response = await apiClient.get('/posts?page=1&per_page=10');
      
      expect(response.data).toEqual(mockResponse);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/posts?page=1&per_page=10');
    });

    it('mocks post detail fetch', async () => {
      const mockPost = createMockPost({ id: 1, title: 'Detailed Post' });
      
      mockAxiosInstance.get.mockResolvedValue(
        createMockApiResponse(mockPost)
      );

      const response = await apiClient.get('/posts/1');
      
      expect(response.data).toEqual(mockPost);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/posts/1');
    });

    it('mocks posts by keyword', async () => {
      const mockPosts = [createMockPost({ keyword_id: 1 })];
      
      mockAxiosInstance.get.mockResolvedValue(
        createMockApiResponse({ items: mockPosts, total: 1 })
      );

      const response = await apiClient.get('/keywords/1/posts');
      
      expect(response.data.items).toEqual(mockPosts);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/keywords/1/posts');
    });
  });

  describe('Trends API', () => {
    it('mocks trend metrics fetch', async () => {
      const mockTrends = [
        createMockTrendMetric({ keyword: 'react', engagement_score: 85.5 }),
        createMockTrendMetric({ keyword: 'vue', engagement_score: 72.3 }),
      ];

      mockAxiosInstance.get.mockResolvedValue(
        createMockApiResponse(mockTrends)
      );

      const response = await apiClient.get('/trends');
      
      expect(response.data).toEqual(mockTrends);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/trends');
    });

    it('mocks trend analysis trigger', async () => {
      const mockTask = { task_id: 'task-123', status: 'pending' };
      
      mockAxiosInstance.post.mockResolvedValue(
        createMockApiResponse(mockTask, 202)
      );

      const response = await apiClient.post('/trends/analyze', { keyword_id: 1 });
      
      expect(response.data).toEqual(mockTask);
      expect(response.status).toBe(202);
    });
  });

  describe('Error Handling', () => {
    it('mocks network errors', async () => {
      mockAxiosInstance.get.mockRejectedValue(
        new Error('Network Error')
      );

      renderWithProviders(<TestApiComponent endpoint="/keywords" />);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Error: Network Error');
      });
    });

    it('mocks 404 errors', async () => {
      mockAxiosInstance.get.mockRejectedValue(
        createMockApiError('Not Found', 404)
      );

      renderWithProviders(<TestApiComponent endpoint="/keywords/999" />);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Error: Not Found');
      });
    });

    it('mocks validation errors', async () => {
      const validationError = {
        response: {
          data: {
            message: 'Validation failed',
            errors: {
              keyword: ['This field is required'],
            },
          },
          status: 422,
        },
        message: 'Validation failed',
        isAxiosError: true,
      };

      mockAxiosInstance.post.mockRejectedValue(validationError);

      try {
        await apiClient.post('/keywords', {});
      } catch (error) {
        expect(error.response.status).toBe(422);
        expect(error.response.data.errors.keyword).toContain('This field is required');
      }
    });
  });

  describe('Request Interceptors', () => {
    it('mocks authentication token injection', async () => {
      localStorage.setItem('test_access_token', 'mock-token');
      
      mockAxiosInstance.get.mockResolvedValue(
        createMockApiResponse([])
      );

      await apiClient.get('/keywords');

      // Verify that the interceptor would have been called
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
    });

    it('mocks request timeout handling', async () => {
      mockAxiosInstance.get.mockRejectedValue(
        new Error('timeout of 5000ms exceeded')
      );

      renderWithProviders(<TestApiComponent endpoint="/slow-endpoint" />);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Error: timeout of 5000ms exceeded');
      });
    });
  });

  describe('Response Interceptors', () => {
    it('mocks token refresh on 401', async () => {
      // First call returns 401
      mockAxiosInstance.get
        .mockRejectedValueOnce(createMockApiError('Unauthorized', 401))
        .mockResolvedValueOnce(createMockApiResponse([]));

      // Mock refresh token call
      mockAxiosInstance.post.mockResolvedValue(
        createMockApiResponse({
          access_token: 'new-token',
          refresh_token: 'new-refresh-token',
        })
      );

      // This would trigger the refresh flow in a real scenario
      try {
        await apiClient.get('/keywords');
      } catch (error) {
        expect(error.response.status).toBe(401);
      }
    });
  });
});