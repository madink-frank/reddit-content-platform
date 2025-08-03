import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../contexts/AuthContext';
import { ThemeProvider } from '../contexts/ThemeContext';
import { NotificationProvider } from '../contexts/NotificationContext';
import { User } from '../types';

// Mock user for testing
export const mockUser: User = {
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  oauth_provider: 'reddit',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// Mock authenticated state
export const mockAuthenticatedState = {
  user: mockUser,
  tokens: {
    access_token: 'test-access-token',
    refresh_token: 'test-refresh-token',
    token_type: 'bearer',
    expires_in: 3600,
  },
};

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[];
  queryClient?: QueryClient;
  authenticated?: boolean;
  user?: User | null;
}

// Custom render function with all providers
export function renderWithProviders(
  ui: React.ReactElement,
  {
    initialEntries = ['/'],
    queryClient,
    authenticated = false,
    user = null,
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  // Create a fresh query client for each test if not provided
  const testQueryClient = queryClient || new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  // Set up authenticated state if needed
  if (authenticated && user) {
    localStorage.setItem('test_user', JSON.stringify(user));
    localStorage.setItem('test_access_token', 'test-access-token');
    localStorage.setItem('test_refresh_token', 'test-refresh-token');
    localStorage.setItem('test_expires_at', (Date.now() + 3600000).toString());
  }

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <BrowserRouter>
        <QueryClientProvider client={testQueryClient}>
          <ThemeProvider>
            <NotificationProvider>
              <AuthProvider>
                {children}
              </AuthProvider>
            </NotificationProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </BrowserRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

// Helper to create mock API responses
export const createMockApiResponse = <T>(data: T, status = 200) => ({
  data,
  status,
  statusText: 'OK',
  headers: {},
  config: {},
});

// Helper to create mock error responses
export const createMockApiError = (message: string, status = 500) => ({
  response: {
    data: { message },
    status,
    statusText: 'Internal Server Error',
  },
  message,
  isAxiosError: true,
});

// Mock data generators
export const createMockKeyword = (overrides = {}) => ({
  id: 1,
  user_id: 1,
  keyword: 'test-keyword',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockPost = (overrides = {}) => ({
  id: 1,
  keyword_id: 1,
  reddit_id: 'test_post_id',
  title: 'Test Post Title',
  content: 'Test post content',
  author: 'test_author',
  score: 100,
  num_comments: 10,
  url: 'https://reddit.com/r/test/comments/test',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockTrendMetric = (overrides = {}) => ({
  id: 1,
  keyword_id: 1,
  keyword: 'test-keyword',
  engagement_score: 85.5,
  tfidf_score: 0.75,
  trend_velocity: 12.3,
  post_count: 25,
  calculated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockBlogContent = (overrides = {}) => ({
  id: 1,
  keyword_id: 1,
  title: 'Test Blog Post',
  content: '# Test Blog Post\n\nThis is test content.',
  template_used: 'default',
  generated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

// Helper to wait for async operations
export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0));

// Helper to simulate user interactions
export const simulateDelay = (ms = 100) => 
  new Promise(resolve => setTimeout(resolve, ms));

// Mock Chart.js chart instance
export const mockChartInstance = {
  destroy: vi.fn(),
  update: vi.fn(),
  resize: vi.fn(),
  render: vi.fn(),
  stop: vi.fn(),
  reset: vi.fn(),
  toBase64Image: vi.fn(() => 'data:image/png;base64,'),
  generateLegend: vi.fn(() => '<ul></ul>'),
  data: { datasets: [] },
  options: {},
};

// Mock Chart.js constructor
export const mockChart = vi.fn().mockImplementation(() => mockChartInstance);

// Helper to mock API endpoints
export const mockApiEndpoints = {
  keywords: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    toggle: vi.fn(),
  },
  posts: {
    list: vi.fn(),
    detail: vi.fn(),
    byKeyword: vi.fn(),
  },
  trends: {
    list: vi.fn(),
    detail: vi.fn(),
  },
  content: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    templates: vi.fn(),
  },
  tasks: {
    list: vi.fn(),
    status: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
  },
  system: {
    health: vi.fn(),
    metrics: vi.fn(),
  },
};

// Helper to reset all API mocks
export const resetApiMocks = () => {
  Object.values(mockApiEndpoints).forEach(endpoint => {
    Object.values(endpoint).forEach(method => {
      if (typeof method === 'function' && 'mockClear' in method) {
        method.mockClear();
      }
    });
  });
};