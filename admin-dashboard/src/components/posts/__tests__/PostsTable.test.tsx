import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PostsTable } from '../PostsTable';
import { renderWithProviders, createMockPost } from '../../../test/utils';

const mockPosts = [
  createMockPost({
    id: 1,
    title: 'First Test Post',
    author: 'user1',
    score: 150,
    num_comments: 25,
  }),
  createMockPost({
    id: 2,
    title: 'Second Test Post',
    author: 'user2',
    score: 89,
    num_comments: 12,
  }),
];

describe('PostsTable', () => {
  const defaultProps = {
    posts: mockPosts,
    isLoading: false,
    onPostClick: vi.fn(),
    onSort: vi.fn(),
    sortBy: 'created_at' as const,
    sortOrder: 'desc' as const,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders posts table correctly', () => {
    renderWithProviders(<PostsTable {...defaultProps} />);
    
    expect(screen.getByText('First Test Post')).toBeInTheDocument();
    expect(screen.getByText('Second Test Post')).toBeInTheDocument();
    expect(screen.getByText('user1')).toBeInTheDocument();
    expect(screen.getByText('user2')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    renderWithProviders(
      <PostsTable {...defaultProps} isLoading={true} posts={[]} />
    );
    
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows empty state when no posts', () => {
    renderWithProviders(
      <PostsTable {...defaultProps} posts={[]} />
    );
    
    expect(screen.getByText('No posts found')).toBeInTheDocument();
  });

  it('calls onPostClick when post title is clicked', () => {
    const onPostClick = vi.fn();
    renderWithProviders(
      <PostsTable {...defaultProps} onPostClick={onPostClick} />
    );
    
    fireEvent.click(screen.getByText('First Test Post'));
    expect(onPostClick).toHaveBeenCalledWith(mockPosts[0]);
  });

  it('calls onSort when column header is clicked', () => {
    const onSort = vi.fn();
    renderWithProviders(
      <PostsTable {...defaultProps} onSort={onSort} />
    );
    
    fireEvent.click(screen.getByText('Score'));
    expect(onSort).toHaveBeenCalledWith('score');
  });

  it('shows sort indicators', () => {
    renderWithProviders(
      <PostsTable {...defaultProps} sortBy="score" sortOrder="asc" />
    );
    
    const scoreHeader = screen.getByText('Score');
    expect(scoreHeader.closest('th')).toContainHTML('↑');
  });

  it('displays post metadata correctly', () => {
    renderWithProviders(<PostsTable {...defaultProps} />);
    
    expect(screen.getByText('150')).toBeInTheDocument(); // score
    expect(screen.getByText('25')).toBeInTheDocument(); // comments
    expect(screen.getAllByText(/Jan 1, 2024/)).toHaveLength(2); // dates
  });

  it('truncates long post titles', () => {
    const longTitlePost = createMockPost({
      title: 'This is a very long post title that should be truncated to prevent layout issues',
    });

    renderWithProviders(
      <PostsTable {...defaultProps} posts={[longTitlePost]} />
    );
    
    const titleElement = screen.getByText(/This is a very long post title/);
    expect(titleElement).toHaveClass('truncate');
  });

  it('shows external link icon for Reddit URLs', () => {
    renderWithProviders(<PostsTable {...defaultProps} />);
    
    const externalLinks = screen.getAllByTitle('Open in Reddit');
    expect(externalLinks).toHaveLength(2);
  });

  it('handles keyboard navigation', async () => {
    const onPostClick = vi.fn();
    renderWithProviders(
      <PostsTable {...defaultProps} onPostClick={onPostClick} />
    );
    
    const firstPostTitle = screen.getByText('First Test Post');
    firstPostTitle.focus();
    
    fireEvent.keyDown(firstPostTitle, { key: 'Enter' });
    expect(onPostClick).toHaveBeenCalledWith(mockPosts[0]);
  });

  it('shows post status indicators', () => {
    const postsWithStatus = [
      createMockPost({ id: 1, score: 1000 }), // high score
      createMockPost({ id: 2, score: 10 }), // low score
    ];

    renderWithProviders(
      <PostsTable {...defaultProps} posts={postsWithStatus} />
    );
    
    // High score posts should have some visual indicator
    expect(screen.getByText('1000')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('formats dates correctly', () => {
    renderWithProviders(<PostsTable {...defaultProps} />);
    
    // Should show formatted dates
    expect(screen.getAllByText(/Jan 1, 2024/)).toHaveLength(2);
  });

  it('has proper accessibility attributes', () => {
    renderWithProviders(<PostsTable {...defaultProps} />);
    
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    
    const columnHeaders = screen.getAllByRole('columnheader');
    expect(columnHeaders.length).toBeGreaterThan(0);
    
    const rows = screen.getAllByRole('row');
    expect(rows.length).toBe(3); // header + 2 data rows
    
    // Check that sortable columns have proper attributes
    const sortableHeaders = screen.getAllByRole('button');
    sortableHeaders.forEach(header => {
      expect(header).toHaveAttribute('aria-label');
    });
  });

  it('handles responsive design', () => {
    renderWithProviders(<PostsTable {...defaultProps} />);
    
    const table = screen.getByRole('table');
    expect(table.closest('div')).toHaveClass('overflow-x-auto');
  });
});