import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SystemHealthCard } from '../SystemHealthCard';
import { renderWithProviders } from '../../../test/utils';

// Mock the hooks
vi.mock('../../../hooks/useSystem', () => ({
  useSystemHealth: vi.fn(),
}));

const mockHealthData = {
  status: 'healthy' as const,
  services: {
    database: { status: 'healthy' as const, response_time: 15 },
    redis: { status: 'healthy' as const, response_time: 5 },
    celery: { status: 'healthy' as const, response_time: 8 },
    reddit_api: { status: 'healthy' as const, response_time: 120 },
  },
  uptime: 86400, // 1 day in seconds
  last_check: '2024-01-01T12:00:00Z',
};

describe('SystemHealthCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders healthy system status', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: mockHealthData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('System Health')).toBeInTheDocument();
    expect(screen.getByText('Healthy')).toBeInTheDocument();
    expect(screen.getByText('All systems operational')).toBeInTheDocument();
  });

  it('renders degraded system status', () => {
    const degradedData = {
      ...mockHealthData,
      status: 'degraded' as const,
      services: {
        ...mockHealthData.services,
        database: { status: 'degraded' as const, response_time: 500 },
      },
    };

    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: degradedData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('Degraded')).toBeInTheDocument();
    expect(screen.getByText('Some services experiencing issues')).toBeInTheDocument();
  });

  it('renders unhealthy system status', () => {
    const unhealthyData = {
      ...mockHealthData,
      status: 'unhealthy' as const,
      services: {
        ...mockHealthData.services,
        database: { status: 'unhealthy' as const, response_time: null },
      },
    };

    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: unhealthyData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('Unhealthy')).toBeInTheDocument();
    expect(screen.getByText('Critical issues detected')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch health data'),
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('Error loading system health')).toBeInTheDocument();
  });

  it('displays service details', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: mockHealthData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('Database')).toBeInTheDocument();
    expect(screen.getByText('Redis')).toBeInTheDocument();
    expect(screen.getByText('Celery')).toBeInTheDocument();
    expect(screen.getByText('Reddit API')).toBeInTheDocument();
    
    expect(screen.getByText('15ms')).toBeInTheDocument();
    expect(screen.getByText('5ms')).toBeInTheDocument();
    expect(screen.getByText('8ms')).toBeInTheDocument();
    expect(screen.getByText('120ms')).toBeInTheDocument();
  });

  it('displays uptime correctly', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: mockHealthData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('1d 0h 0m')).toBeInTheDocument();
  });

  it('shows last check time', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: mockHealthData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText(/Last check:/)).toBeInTheDocument();
  });

  it('uses correct status colors', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: mockHealthData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    const healthyBadge = screen.getByText('Healthy');
    expect(healthyBadge).toHaveClass('bg-green-100', 'text-green-800');
  });

  it('handles missing response times', () => {
    const dataWithNullTimes = {
      ...mockHealthData,
      services: {
        ...mockHealthData.services,
        database: { status: 'unhealthy' as const, response_time: null },
      },
    };

    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: dataWithNullTimes,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    expect(screen.getByText('N/A')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    vi.mocked(require('../../../hooks/useSystem').useSystemHealth).mockReturnValue({
      data: mockHealthData,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<SystemHealthCard />);
    
    const card = screen.getByRole('region');
    expect(card).toHaveAttribute('aria-label', 'System health status');
    
    const statusBadge = screen.getByText('Healthy');
    expect(statusBadge).toHaveAttribute('aria-label', 'System status: Healthy');
  });
});