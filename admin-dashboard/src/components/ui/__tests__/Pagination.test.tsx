import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from '../Pagination';

describe('Pagination', () => {
  const defaultProps = {
    currentPage: 1,
    totalPages: 10,
    onPageChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders pagination controls', () => {
    render(<Pagination {...defaultProps} />);
    
    expect(screen.getByText('Previous')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('disables previous button on first page', () => {
    render(<Pagination {...defaultProps} currentPage={1} />);
    
    const prevButton = screen.getByText('Previous');
    expect(prevButton.closest('button')).toBeDisabled();
  });

  it('disables next button on last page', () => {
    render(<Pagination {...defaultProps} currentPage={10} totalPages={10} />);
    
    const nextButton = screen.getByText('Next');
    expect(nextButton.closest('button')).toBeDisabled();
  });

  it('calls onPageChange when page number is clicked', () => {
    const onPageChange = vi.fn();
    render(<Pagination {...defaultProps} onPageChange={onPageChange} />);
    
    fireEvent.click(screen.getByText('2'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('calls onPageChange when previous button is clicked', () => {
    const onPageChange = vi.fn();
    render(<Pagination {...defaultProps} currentPage={5} onPageChange={onPageChange} />);
    
    fireEvent.click(screen.getByText('Previous'));
    expect(onPageChange).toHaveBeenCalledWith(4);
  });

  it('calls onPageChange when next button is clicked', () => {
    const onPageChange = vi.fn();
    render(<Pagination {...defaultProps} currentPage={5} onPageChange={onPageChange} />);
    
    fireEvent.click(screen.getByText('Next'));
    expect(onPageChange).toHaveBeenCalledWith(6);
  });

  it('shows ellipsis for large page ranges', () => {
    render(<Pagination {...defaultProps} currentPage={5} totalPages={20} />);
    
    expect(screen.getByText('...')).toBeInTheDocument();
  });

  it('highlights current page', () => {
    render(<Pagination {...defaultProps} currentPage={3} />);
    
    const currentPageButton = screen.getByText('3');
    expect(currentPageButton.closest('button')).toHaveClass('bg-indigo-600', 'text-white');
  });

  it('shows page info when showInfo is true', () => {
    render(<Pagination {...defaultProps} showInfo={true} totalItems={100} itemsPerPage={10} />);
    
    expect(screen.getByText(/Showing \d+ to \d+ of \d+ results/)).toBeInTheDocument();
  });

  it('handles single page correctly', () => {
    render(<Pagination {...defaultProps} totalPages={1} />);
    
    const prevButton = screen.getByText('Previous');
    const nextButton = screen.getByText('Next');
    
    expect(prevButton.closest('button')).toBeDisabled();
    expect(nextButton.closest('button')).toBeDisabled();
  });

  it('has proper accessibility attributes', () => {
    render(<Pagination {...defaultProps} />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveAttribute('aria-label', 'Pagination');
    
    const currentPageButton = screen.getByText('1');
    expect(currentPageButton.closest('button')).toHaveAttribute('aria-current', 'page');
  });
});