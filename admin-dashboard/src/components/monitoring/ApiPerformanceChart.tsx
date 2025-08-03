import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { SystemMetrics } from '../../services/api/systemApi';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ApiPerformanceChartProps {
  metrics: SystemMetrics[];
  isLoading?: boolean;
  chartType?: 'line' | 'bar';
}

const ApiPerformanceChart: React.FC<ApiPerformanceChartProps> = ({ 
  metrics, 
  isLoading, 
  chartType = 'line' 
}) => {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!metrics || metrics.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          API Performance
        </h3>
        <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
          No performance data available
        </div>
      </div>
    );
  }

  const labels = metrics.map(metric => 
    new Date(metric.timestamp).toLocaleTimeString()
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Response Time (ms)',
        data: metrics.map(m => m.api_response_time_avg * 1000), // Convert to ms
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: chartType === 'bar' ? 'rgba(239, 68, 68, 0.8)' : 'rgba(239, 68, 68, 0.1)',
        fill: chartType === 'line',
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'Request Count',
        data: metrics.map(m => m.api_requests_total),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: chartType === 'bar' ? 'rgba(34, 197, 94, 0.8)' : 'rgba(34, 197, 94, 0.1)',
        fill: chartType === 'line',
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgb(107, 114, 128)',
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: 'API Performance Metrics',
        color: 'rgb(107, 114, 128)',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.datasetIndex === 0) {
              label += Math.round(context.parsed.y * 100) / 100 + ' ms';
            } else {
              label += context.parsed.y + ' requests';
            }
            return label;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(107, 114, 128, 0.1)',
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(107, 114, 128, 0.1)',
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
          callback: function(value: any) {
            return value + ' ms';
          },
        },
        title: {
          display: true,
          text: 'Response Time (ms)',
          color: 'rgb(107, 114, 128)',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
        },
        title: {
          display: true,
          text: 'Request Count',
          color: 'rgb(107, 114, 128)',
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  const ChartComponent = chartType === 'bar' ? Bar : Line;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="h-80">
        <ChartComponent data={chartData} options={options} />
      </div>
    </div>
  );
};

export default ApiPerformanceChart;