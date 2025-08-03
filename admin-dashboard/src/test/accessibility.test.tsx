import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'vitest-axe';
import { KeywordList } from '../components/keywords/KeywordList';
import { PostsTable } from '../components/posts/PostsTable';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Pagination } from '../components/ui/Pagination';
import { SystemHealthCard } from '../components/monitoring/SystemHealthCard';
import { 
  renderWithProviders, 
  createMockKeyword, 
  createMockPost,
  mockUser 
} from './utils';

// Extend expect with axe matchers
expect.extend(toHaveNoViolations);

// Mock hooks
vi.mock('../hooks/useKeywords', () => ({
  useToggleKeyword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useDeleteKeyword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

vi.mock('../hooks/useSystem', () => ({
  useSystemHealth: () => ({
    data: {
      status: 'healthy',
      services: {
        database: { status: 'healthy', response_time: 15 },
        redis: { status: 'healthy', response_time: 5 },
      },
      uptime: 86400,
      last_check: '2024-01-01T12:00:00Z',
    },
    isLoading: false,
    error: null,
  }),
}));

describe('Accessibility Tests', () => {
  describe('KeywordList Component', () => {
    const mockKeywords = [
      createMockKeyword({ id: 1, keyword: 'react' }),
      createMockKeyword({ id: 2, keyword: 'javascript' }),
    ];

    const defaultProps = {
      keywords: mockKeywords,
      isLoading: false,
      searchQuery: '',
      onSearchChange: vi.fn(),
      onEdit: vi.fn(),
      onAdd: vi.fn(),
      activeFilter: 'all' as const,
      onFilterChange: vi.fn(),
    };

    it('should not have accessibility violations', async () => {
      const { container } = renderWithProviders(
        <KeywordList {...defaultProps} />
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels for interactive elements', () => {
      const { container } = renderWithProviders(
        <KeywordList {...defaultProps} />
      );
      
      const editButtons = container.querySelectorAll('[title="Edit keyword"]');
      editButtons.forEach(button => {
        expect(button).toHaveAttribute('aria-label');
      });
      
      const deleteButtons = container.querySelectorAll('[title="Delete keyword"]');
      deleteButtons.forEach(button => {
        expect(button).toHaveAttribute('aria-label');
      });
    });

    it('should have proper heading structure', () => {
      const { container } = renderWithProviders(
        <KeywordList {...defaultProps} />
      );
      
      const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
      expect(headings.length).toBeGreaterThan(0);
    });

    it('should support keyboard navigation', () => {
      const { container } = renderWithProviders(
        <KeywordList {...defaultProps} />
      );
      
      const interactiveElements = container.querySelectorAll('button, input, select, textarea, a');
      interactiveElements.forEach(element => {
        expect(element).not.toHaveAttribute('tabindex', '-1');
      });
    });
  });

  describe('PostsTable Component', () => {
    const mockPosts = [
      createMockPost({ id: 1, title: 'First Post' }),
      createMockPost({ id: 2, title: 'Second Post' }),
    ];

    const defaultProps = {
      posts: mockPosts,
      isLoading: false,
      onPostClick: vi.fn(),
      onSort: vi.fn(),
      sortBy: 'created_at' as const,
      sortOrder: 'desc' as const,
    };

    it('should not have accessibility violations', async () => {
      const { container } = renderWithProviders(
        <PostsTable {...defaultProps} />
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper table structure', () => {
      const { container } = renderWithProviders(
        <PostsTable {...defaultProps} />
      );
      
      const table = container.querySelector('table');
      expect(table).toBeInTheDocument();
      
      const thead = container.querySelector('thead');
      expect(thead).toBeInTheDocument();
      
      const tbody = container.querySelector('tbody');
      expect(tbody).toBeInTheDocument();
      
      const headers = container.querySelectorAll('th');
      expect(headers.length).toBeGreaterThan(0);
    });

    it('should have sortable columns with proper ARIA attributes', () => {
      const { container } = renderWithProviders(
        <PostsTable {...defaultProps} />
      );
      
      const sortableHeaders = container.querySelectorAll('th button');
      sortableHeaders.forEach(header => {
        expect(header).toHaveAttribute('aria-label');
      });
    });
  });

  describe('LoadingSpinner Component', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<LoadingSpinner />);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA attributes', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveAttribute('aria-label', 'Loading');
      
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Pagination Component', () => {
    const defaultProps = {
      currentPage: 1,
      totalPages: 10,
      onPageChange: vi.fn(),
    };

    it('should not have accessibility violations', async () => {
      const { container } = render(<Pagination {...defaultProps} />);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper navigation structure', () => {
      const { container } = render(<Pagination {...defaultProps} />);
      
      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();
      expect(nav).toHaveAttribute('aria-label', 'Pagination');
    });

    it('should indicate current page', () => {
      const { container } = render(<Pagination {...defaultProps} />);
      
      const currentPage = container.querySelector('[aria-current="page"]');
      expect(currentPage).toBeInTheDocument();
    });

    it('should have proper button states', () => {
      const { container } = render(<Pagination {...defaultProps} currentPage={1} />);
      
      const prevButton = container.querySelector('button:first-child');
      expect(prevButton).toBeDisabled();
      expect(prevButton).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('SystemHealthCard Component', () => {
    it('should not have accessibility violations', async () => {
      const { container } = renderWithProviders(<SystemHealthCard />);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper region structure', () => {
      const { container } = renderWithProviders(<SystemHealthCard />);
      
      const region = container.querySelector('[role="region"]');
      expect(region).toBeInTheDocument();
      expect(region).toHaveAttribute('aria-label', 'System health status');
    });

    it('should have descriptive status indicators', () => {
      const { container } = renderWithProviders(<SystemHealthCard />);
      
      const statusBadge = container.querySelector('[aria-label*="System status"]');
      expect(statusBadge).toBeInTheDocument();
    });
  });

  describe('Color Contrast', () => {
    it('should have sufficient color contrast for text elements', async () => {
      const { container } = renderWithProviders(
        <div>
          <h1 className="text-gray-900">Main Heading</h1>
          <p className="text-gray-600">Body text</p>
          <button className="bg-indigo-600 text-white">Primary Button</button>
          <button className="bg-gray-200 text-gray-900">Secondary Button</button>
        </div>
      );
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      expect(results).toHaveNoViolations();
    });
  });

  describe('Focus Management', () => {
    it('should have visible focus indicators', async () => {
      const { container } = render(
        <div>
          <button className="focus:ring-2 focus:ring-indigo-500">Focusable Button</button>
          <input className="focus:ring-2 focus:ring-indigo-500" />
          <a href="#" className="focus:ring-2 focus:ring-indigo-500">Focusable Link</a>
        </div>
      );
      
      const results = await axe(container, {
        rules: {
          'focus-order-semantics': { enabled: true },
        },
      });
      
      expect(results).toHaveNoViolations();
    });
  });

  describe('Form Accessibility', () => {
    it('should have proper form labels and associations', async () => {
      const { container } = render(
        <form>
          <label htmlFor="keyword-input">Keyword</label>
          <input id="keyword-input" type="text" required />
          
          <fieldset>
            <legend>Status</legend>
            <input type="radio" id="active" name="status" value="active" />
            <label htmlFor="active">Active</label>
            <input type="radio" id="inactive" name="status" value="inactive" />
            <label htmlFor="inactive">Inactive</label>
          </fieldset>
          
          <button type="submit">Submit</button>
        </form>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Image Accessibility', () => {
    it('should have proper alt text for images', async () => {
      const { container } = render(
        <div>
          <img src="/test.jpg" alt="Test image description" />
          <img src="/decorative.jpg" alt="" role="presentation" />
        </div>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Responsive Design Accessibility', () => {
    it('should maintain accessibility at different viewport sizes', async () => {
      // Test mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      const { container } = renderWithProviders(
        <div className="responsive-component">
          <nav className="hidden md:block">Desktop Navigation</nav>
          <nav className="md:hidden">Mobile Navigation</nav>
          <main>Content</main>
        </div>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});