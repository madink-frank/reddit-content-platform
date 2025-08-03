import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MarkdownEditor } from '../MarkdownEditor';
import { renderWithProviders } from '../../../test/utils';

describe('MarkdownEditor', () => {
  const defaultProps = {
    value: '# Test Content\n\nThis is test content.',
    onChange: vi.fn(),
    placeholder: 'Enter markdown content...',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders editor with initial value', () => {
    renderWithProviders(<MarkdownEditor {...defaultProps} />);
    
    expect(screen.getByDisplayValue(/# Test Content/)).toBeInTheDocument();
  });

  it('shows preview when preview tab is clicked', async () => {
    renderWithProviders(<MarkdownEditor {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Preview'));
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Test Content');
      expect(screen.getByText('This is test content.')).toBeInTheDocument();
    });
  });

  it('switches between edit and preview modes', async () => {
    renderWithProviders(<MarkdownEditor {...defaultProps} />);
    
    // Start in edit mode
    expect(screen.getByDisplayValue(/# Test Content/)).toBeInTheDocument();
    
    // Switch to preview
    fireEvent.click(screen.getByText('Preview'));
    await waitFor(() => {
      expect(screen.queryByDisplayValue(/# Test Content/)).not.toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    });
    
    // Switch back to edit
    fireEvent.click(screen.getByText('Edit'));
    await waitFor(() => {
      expect(screen.getByDisplayValue(/# Test Content/)).toBeInTheDocument();
    });
  });

  it('calls onChange when content is modified', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} onChange={onChange} />
    );
    
    const textarea = screen.getByDisplayValue(/# Test Content/);
    await user.clear(textarea);
    await user.type(textarea, '# New Content');
    
    expect(onChange).toHaveBeenCalledWith('# New Content');
  });

  it('shows toolbar buttons', () => {
    renderWithProviders(<MarkdownEditor {...defaultProps} />);
    
    expect(screen.getByTitle('Bold')).toBeInTheDocument();
    expect(screen.getByTitle('Italic')).toBeInTheDocument();
    expect(screen.getByTitle('Heading')).toBeInTheDocument();
    expect(screen.getByTitle('Link')).toBeInTheDocument();
    expect(screen.getByTitle('Code')).toBeInTheDocument();
    expect(screen.getByTitle('List')).toBeInTheDocument();
  });

  it('inserts bold formatting when bold button is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value="" onChange={onChange} />
    );
    
    const textarea = screen.getByRole('textbox');
    await user.click(textarea);
    
    fireEvent.click(screen.getByTitle('Bold'));
    
    expect(onChange).toHaveBeenCalledWith('**bold text**');
  });

  it('inserts italic formatting when italic button is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value="" onChange={onChange} />
    );
    
    const textarea = screen.getByRole('textbox');
    await user.click(textarea);
    
    fireEvent.click(screen.getByTitle('Italic'));
    
    expect(onChange).toHaveBeenCalledWith('*italic text*');
  });

  it('inserts heading when heading button is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value="" onChange={onChange} />
    );
    
    const textarea = screen.getByRole('textbox');
    await user.click(textarea);
    
    fireEvent.click(screen.getByTitle('Heading'));
    
    expect(onChange).toHaveBeenCalledWith('# Heading');
  });

  it('inserts link when link button is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value="" onChange={onChange} />
    );
    
    const textarea = screen.getByRole('textbox');
    await user.click(textarea);
    
    fireEvent.click(screen.getByTitle('Link'));
    
    expect(onChange).toHaveBeenCalledWith('[link text](url)');
  });

  it('handles keyboard shortcuts', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value="" onChange={onChange} />
    );
    
    const textarea = screen.getByRole('textbox');
    await user.click(textarea);
    
    // Test Ctrl+B for bold
    await user.keyboard('{Control>}b{/Control}');
    
    expect(onChange).toHaveBeenCalledWith('**bold text**');
  });

  it('shows character count when enabled', () => {
    renderWithProviders(
      <MarkdownEditor {...defaultProps} showCharCount={true} />
    );
    
    expect(screen.getByText(/\d+ characters/)).toBeInTheDocument();
  });

  it('applies custom height', () => {
    renderWithProviders(
      <MarkdownEditor {...defaultProps} height="400px" />
    );
    
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveStyle({ height: '400px' });
  });

  it('handles empty content', () => {
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value="" />
    );
    
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveValue('');
    expect(textarea).toHaveAttribute('placeholder', 'Enter markdown content...');
  });

  it('renders code blocks correctly in preview', async () => {
    const codeContent = '```javascript\nconsole.log("Hello World");\n```';
    
    renderWithProviders(
      <MarkdownEditor {...defaultProps} value={codeContent} />
    );
    
    fireEvent.click(screen.getByText('Preview'));
    
    await waitFor(() => {
      expect(screen.getByText('console.log("Hello World");')).toBeInTheDocument();
    });
  });

  it('has proper accessibility attributes', () => {
    renderWithProviders(<MarkdownEditor {...defaultProps} />);
    
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('aria-label', 'Markdown editor');
    
    const tablist = screen.getByRole('tablist');
    expect(tablist).toBeInTheDocument();
    
    const tabs = screen.getAllByRole('tab');
    expect(tabs).toHaveLength(2);
    expect(tabs[0]).toHaveAttribute('aria-selected', 'true');
  });
});