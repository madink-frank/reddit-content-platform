import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { KeywordList } from '../components/keywords/KeywordList';
import { KeywordForm } from '../components/keywords/KeywordForm';
import { Keyword } from '../types';

// Mock the hooks
vi.mock('../hooks/useKeywords', () => ({
  useToggleKeyword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useDeleteKeyword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useCreateKeyword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useUpdateKeyword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

const mockKeywords: Keyword[] = [
  {
    id: 1,
    user_id: 1,
    keyword: 'react',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    user_id: 1,
    keyword: 'javascript',
    is_active: false,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('KeywordList', () => {
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

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders keywords list correctly', () => {
    renderWithQueryClient(<KeywordList {...defaultProps} />);
    
    expect(screen.getByText('react')).toBeInTheDocument();
    expect(screen.getByText('javascript')).toBeInTheDocument();
    expect(screen.getAllByText('Active')).toHaveLength(2); // Badge and toggle label
    expect(screen.getAllByText('Inactive')).toHaveLength(2); // Badge and toggle label
  });

  it('shows loading state', () => {
    renderWithQueryClient(
      <KeywordList {...defaultProps} isLoading={true} keywords={[]} />
    );
    
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows empty state when no keywords', () => {
    renderWithQueryClient(
      <KeywordList {...defaultProps} keywords={[]} />
    );
    
    expect(screen.getByText('No keywords yet')).toBeInTheDocument();
    expect(screen.getByText('Get started by adding your first keyword.')).toBeInTheDocument();
  });

  it('filters keywords by search query', () => {
    renderWithQueryClient(
      <KeywordList {...defaultProps} searchQuery="react" />
    );
    
    expect(screen.getByText('react')).toBeInTheDocument();
    expect(screen.queryByText('javascript')).not.toBeInTheDocument();
  });

  it('calls onAdd when add button is clicked', () => {
    const onAdd = vi.fn();
    renderWithQueryClient(
      <KeywordList {...defaultProps} onAdd={onAdd} />
    );
    
    fireEvent.click(screen.getByText('Add Keyword'));
    expect(onAdd).toHaveBeenCalled();
  });

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn();
    renderWithQueryClient(
      <KeywordList {...defaultProps} onEdit={onEdit} />
    );
    
    const editButtons = screen.getAllByTitle('Edit keyword');
    fireEvent.click(editButtons[0]);
    expect(onEdit).toHaveBeenCalledWith(mockKeywords[0]);
  });
});

describe('KeywordForm', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders create form correctly', () => {
    renderWithQueryClient(<KeywordForm {...defaultProps} />);
    
    expect(screen.getByText('Add New Keyword')).toBeInTheDocument();
    expect(screen.getByLabelText(/Keyword/)).toBeInTheDocument();
    expect(screen.getByText('Create')).toBeInTheDocument();
  });

  it('renders edit form correctly', () => {
    renderWithQueryClient(
      <KeywordForm {...defaultProps} keyword={mockKeywords[0]} />
    );
    
    expect(screen.getByText('Edit Keyword')).toBeInTheDocument();
    expect(screen.getByDisplayValue('react')).toBeInTheDocument();
    expect(screen.getByText('Update')).toBeInTheDocument();
  });

  it('validates required keyword field', async () => {
    renderWithQueryClient(<KeywordForm {...defaultProps} />);
    
    const submitButton = screen.getByText('Create');
    expect(submitButton).toBeDisabled();
    
    const keywordInput = screen.getByLabelText(/Keyword/);
    fireEvent.change(keywordInput, { target: { value: 'test' } });
    
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('shows validation error for invalid characters', async () => {
    renderWithQueryClient(<KeywordForm {...defaultProps} />);
    
    const keywordInput = screen.getByLabelText(/Keyword/);
    fireEvent.change(keywordInput, { target: { value: 'test@#$' } });
    
    await waitFor(() => {
      expect(screen.getByText(/Only letters, numbers, spaces, hyphens, and underscores are allowed/)).toBeInTheDocument();
    });
  });

  it('calls onClose when cancel button is clicked', () => {
    const onClose = vi.fn();
    renderWithQueryClient(
      <KeywordForm {...defaultProps} onClose={onClose} />
    );
    
    fireEvent.click(screen.getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('does not render when isOpen is false', () => {
    renderWithQueryClient(
      <KeywordForm {...defaultProps} isOpen={false} />
    );
    
    expect(screen.queryByText('Add New Keyword')).not.toBeInTheDocument();
  });
});