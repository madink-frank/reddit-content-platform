import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CrawlingControlPanel from '../CrawlingControlPanel';

// Mock the hooks
vi.mock('../../../hooks/useKeywords', () => ({
  useKeywords: () => ({
    data: {
      items: [
        { id: 1, keyword: 'test-keyword', is_active: true },
        { id: 2, keyword: 'inactive-keyword', is_active: false },
      ]
    }
  })
}));

vi.mock('../../../hooks/useCrawling', () => ({
  useStartKeywordCrawl: () => ({ mutate: vi.fn(), isPending: false }),
  useStartAllKeywordsCrawl: () => ({ mutate: vi.fn(), isPending: false }),
  useStartSubredditCrawl: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock('../../../stores/notificationStore', () => ({
  useNotificationStore: () => ({
    addNotification: vi.fn(),
  }),
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('CrawlingControlPanel', () => {
  it('renders crawling controls', () => {
    renderWithQueryClient(<CrawlingControlPanel />);
    
    expect(screen.getByText('Crawling Controls')).toBeInTheDocument();
    expect(screen.getByText('Single Keyword Crawling')).toBeInTheDocument();
    expect(screen.getByText('All Keywords Crawling')).toBeInTheDocument();
    expect(screen.getByText('Subreddit Crawling')).toBeInTheDocument();
  });

  it('shows active keywords in select options', () => {
    renderWithQueryClient(<CrawlingControlPanel />);
    
    // Should show the active keyword but not the inactive one (appears in both select elements)
    expect(screen.getAllByText('test-keyword')).toHaveLength(2); // Single keyword and subreddit selects
    expect(screen.queryByText('inactive-keyword')).not.toBeInTheDocument();
  });

  it('displays start crawl buttons', () => {
    renderWithQueryClient(<CrawlingControlPanel />);
    
    expect(screen.getByText('Start Keyword Crawl')).toBeInTheDocument();
    expect(screen.getByText('Start All Keywords Crawl')).toBeInTheDocument();
    expect(screen.getByText('Start Subreddit Crawl')).toBeInTheDocument();
  });
});