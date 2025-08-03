import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from '../services/apiClient';
import { queryKeys } from '../services/queryClient';

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

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Query Keys', () => {
    it('should generate correct query keys for keywords', () => {
      expect(queryKeys.keywords.all).toEqual(['keywords']);
      expect(queryKeys.keywords.list(1)).toEqual(['keywords', 'list', 1]);
      expect(queryKeys.keywords.detail(123)).toEqual(['keywords', 'detail', 123]);
    });

    it('should generate correct query keys for posts', () => {
      expect(queryKeys.posts.all).toEqual(['posts']);
      expect(queryKeys.posts.list({ page: 1 })).toEqual(['posts', 'list', { page: 1 }]);
      expect(queryKeys.posts.detail(456)).toEqual(['posts', 'detail', 456]);
      expect(queryKeys.posts.byKeyword(123, { page: 2 })).toEqual([
        'posts',
        'byKeyword',
        123,
        { page: 2 },
      ]);
    });

    it('should generate correct query keys for trends', () => {
      expect(queryKeys.trends.all).toEqual(['trends']);
      expect(queryKeys.trends.list({ time_range: '24h' })).toEqual([
        'trends',
        'list',
        { time_range: '24h' },
      ]);
      expect(queryKeys.trends.detail(789)).toEqual(['trends', 'detail', 789]);
    });

    it('should generate correct query keys for content', () => {
      expect(queryKeys.content.all).toEqual(['content']);
      expect(queryKeys.content.list({ page: 1 })).toEqual(['content', 'list', { page: 1 }]);
      expect(queryKeys.content.detail(101)).toEqual(['content', 'detail', 101]);
      expect(queryKeys.content.templates).toEqual(['content', 'templates']);
    });

    it('should generate correct query keys for tasks', () => {
      expect(queryKeys.tasks.all).toEqual(['tasks']);
      expect(queryKeys.tasks.list({ status: 'running' })).toEqual([
        'tasks',
        'list',
        { status: 'running' },
      ]);
      expect(queryKeys.tasks.status('task-123')).toEqual(['tasks', 'status', 'task-123']);
    });

    it('should generate correct query keys for system', () => {
      expect(queryKeys.system.health).toEqual(['system', 'health']);
      expect(queryKeys.system.metrics('1h')).toEqual(['system', 'metrics', '1h']);
    });
  });

  describe('API Client Instance', () => {
    it('should be defined', () => {
      expect(apiClient).toBeDefined();
    });

    it('should have HTTP methods', () => {
      expect(typeof apiClient.get).toBe('function');
      expect(typeof apiClient.post).toBe('function');
      expect(typeof apiClient.put).toBe('function');
      expect(typeof apiClient.patch).toBe('function');
      expect(typeof apiClient.delete).toBe('function');
    });

    it('should have loading-aware HTTP methods', () => {
      expect(typeof apiClient.getWithLoading).toBe('function');
      expect(typeof apiClient.postWithLoading).toBe('function');
      expect(typeof apiClient.putWithLoading).toBe('function');
      expect(typeof apiClient.deleteWithLoading).toBe('function');
    });

    it('should have getInstance method', () => {
      expect(typeof apiClient.getInstance).toBe('function');
    });
  });
});