import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import TrendChart from '../TrendChart';
import { TrendMetrics } from '../../../types';

// Mock Chart.js
vi.mock('react-chartjs-2', () => ({
  Line: ({ data, options }: any) => (
    <div data-testid="trend-chart">
      <div data-testid="chart-title">{options?.plugins?.title?.text}</div>
      <div data-testid="chart-datasets">{JSON.stringify(data.datasets)}</div>
    </div>
  ),
}));

const mockTrendData: TrendMetrics[] = [
  {
    id: 1,
    post_id: 1,
    engagement_score: 0.75,
    tfidf_score: 0.85,
    trend_velocity: 0.65,
    calculated_at: '2024-01-01T12:00:00Z',
  },
  {
    id: 2,
    post_id: 2,
    engagement_score: 0.80,
    tfidf_score: 0.90,
    trend_velocity: 0.70,
    calculated_at: '2024-01-01T13:00:00Z',
  },
];

describe('TrendChart', () => {
  it('renders chart with data', () => {
    render(
      <TrendChart
        data={mockTrendData}
        title="Test Trend Chart"
      />
    );

    expect(screen.getByTestId('trend-chart')).toBeInTheDocument();
    expect(screen.getByTestId('chart-title')).toHaveTextContent('Test Trend Chart');
  });

  it('shows empty state when no data', () => {
    render(<TrendChart data={[]} />);

    expect(screen.getByText('No trend data available')).toBeInTheDocument();
    expect(screen.getByText('Run trend analysis to see charts')).toBeInTheDocument();
  });

  it('includes all metrics by default', () => {
    render(<TrendChart data={mockTrendData} />);

    const datasets = screen.getByTestId('chart-datasets');
    const datasetsData = JSON.parse(datasets.textContent || '[]');
    
    expect(datasetsData).toHaveLength(3); // engagement, tfidf, velocity
    expect(datasetsData.some((d: any) => d.label === 'Engagement Score')).toBe(true);
    expect(datasetsData.some((d: any) => d.label === 'TF-IDF Score')).toBe(true);
    expect(datasetsData.some((d: any) => d.label === 'Trend Velocity')).toBe(true);
  });

  it('can hide specific metrics', () => {
    render(
      <TrendChart
        data={mockTrendData}
        showEngagement={true}
        showTfIdf={false}
        showVelocity={false}
      />
    );

    const datasets = screen.getByTestId('chart-datasets');
    const datasetsData = JSON.parse(datasets.textContent || '[]');
    
    expect(datasetsData).toHaveLength(1);
    expect(datasetsData[0].label).toBe('Engagement Score');
  });
});