import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ContentList } from '../ContentList';
import { renderWithProviders, createMockBlogContent } from '../../../test/utils';

// Mock the hooks
vi.mock('../../../hooks/useContent', () => ({
  useDeleteContent: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

const mockContent = [
  createMockBlogContent({
    id: 1,
    title: 'First Blog Post',
    content: '# First Post\n\nThis is the first post.',
  }),
  createMockBlogContent({
    id: 2,
    title: 'Second Blog Post',
    content: '# Second Post\n\nThis is the second post.',
  }),
];

describe('ContentList', () => {
  const defaultProps = {
    content: mockContent,
    isLoading: false,
    onEdit: vi.fn(),
    onView: vi.fn(),
    onGenerate: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders content list correctly', () => {
    renderWithProviders(<ContentList {...defaultProps} />);
    
    expect(screen.getByText('First Blog Post')).toBeInTheDocument();
    expect(screen.getByText('Second Blog Post')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    renderWithProviders(
      <ContentList {...defaultProps} isLoading={true} content={[]} />
    );
    
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows empty state when no content', () => {
    renderWithProviders(
      <ContentList {...defaultProps} content={[]} />
    );
    
    expect(screen.getByText('No content generated yet')).toBeInTheDocument();
    expect(screen.getByText('Generate your first blog post to get started.')).toBeInTheDocument();
  });

  it('calls onView when view button is clicked', () => {
    const onView = vi.fn();
    renderWithProviders(
      <ContentList {...defaultProps} onView={onView} />
    );
    
    const viewButtons = screen.getAllByTitle('View content');
    fireEvent.click(viewButtons[0]);
    
    expect(onView).toHaveBeenCalledWith(mockContent[0]);
  });

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn();
    renderWithProviders(
      <ContentList {...defaultProps} onEdit={onEdit} />
    );
    
    const editButtons = screen.getAllByTitle('Edit content');
    fireEvent.click(editButtons[0]);
    
    expect(onEdit).toHaveBeenCalledWith(mockContent[0]);
  });

  it('calls onGenerate when generate button is clicked', () => {
    const onGenerate = vi.fn();
    renderWithProviders(
      <ContentList {...defaultProps} onGenerate={onGenerate} />
    );
    
    fireEvent.click(screen.getByText('Generate New Content'));
    expect(onGenerate).toHaveBeenCalled();
  });

  it('shows delete confirmation dialog', async () => {
    renderWithProviders(<ContentList {...defaultProps} />);
    
    const deleteButtons = screen.getAllByTitle('Delete content');
    fireEvent.click(deleteButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByText('Delete Content')).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument();
    });
  });

  it('handles delete confirmation', async () => {
    const mockDeleteContent = vi.fn().mockResolvedValue({});
    vi.mocked(require('../../../hooks/useContent').useDeleteContent).mockReturnValue({
      mutateAsync: mockDeleteContent,
      isPending: false,
    });

    renderWithProviders(<ContentList {...defaultProps} />);
    
    const deleteButtons = screen.getAllByTitle('Delete content');
    fireEvent.click(deleteButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByText('Delete Content')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Delete'));
    
    await waitFor(() => {
      expect(mockDeleteContent).toHaveBeenCalledWith(1);
    });
  });

  it('displays content metadata correctly', () => {
    renderWithProviders(<ContentList {...defaultProps} />);
    
    expect(screen.getByText('default')).toBeInTheDocument(); // template
    expect(screen.getAllByText(/Jan 1, 2024/)).toHaveLength(2); // dates
  });

  it('truncates long content previews', () => {
    const longContent = createMockBlogContent({
      content: '# Long Post\n\n' + 'This is a very long content that should be truncated. '.repeat(20),
    });

    renderWithProviders(
      <ContentList {...defaultProps} content={[longContent]} />
    );
    
    const contentPreview = screen.getByText(/This is a very long content/);
    expect(contentPreview.textContent?.length).toBeLessThan(longContent.content.length);
  });

  it('has proper accessibility attributes', () => {
    renderWithProviders(<ContentList {...defaultProps} />);
    
    const list = screen.getByRole('list');
    expect(list).toBeInTheDocument();
    
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(2);
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('title');
    });
  });
});