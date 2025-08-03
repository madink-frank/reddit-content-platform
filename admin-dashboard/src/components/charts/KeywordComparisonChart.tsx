import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import { TrendData } from '../../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

interface KeywordComparisonChartProps {
  trendsData: TrendData[];
  metric: 'engagement_score' | 'tfidf_score' | 'trend_velocity';
  title?: string;
  height?: number;
}

const KeywordComparisonChart: React.FC<KeywordComparisonChartProps> = ({
  trendsData,
  metric,
  title,
  height = 400,
}) => {
  const colors = [
    'rgb(59, 130, 246)',   // Blue
    'rgb(16, 185, 129)',   // Green
    'rgb(245, 101, 101)',  // Red
    'rgb(245, 158, 11)',   // Yellow
    'rgb(139, 92, 246)',   // Purple
    'rgb(236, 72, 153)',   // Pink
    'rgb(6, 182, 212)',    // Cyan
    'rgb(34, 197, 94)',    // Emerald
  ];

  const getMetricLabel = (metric: string) => {
    switch (metric) {
      case 'engagement_score':
        return 'Engagement Score';
      case 'tfidf_score':
        return 'TF-IDF Score';
      case 'trend_velocity':
        return 'Trend Velocity';
      default:
        return metric;
    }
  };

  const chartData = {
    datasets: trendsData.map((trendData, index) => {
      const color = colors[index % colors.length];
      return {
        label: trendData.keyword,
        data: trendData.metrics.map((item) => ({
          x: new Date(item.calculated_at),
          y: item[metric],
        })),
        borderColor: color,
        backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
      };
    }),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      title: {
        display: !!title,
        text: title || `Keyword Comparison - ${getMetricLabel(metric)}`,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
        padding: {
          bottom: 20,
        },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          title: (context: any) => {
            return new Date(context[0].parsed.x).toLocaleString();
          },
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y.toFixed(4);
            return `${label}: ${value}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          displayFormats: {
            hour: 'MMM dd HH:mm',
            day: 'MMM dd',
            week: 'MMM dd',
            month: 'MMM yyyy',
          },
        },
        title: {
          display: true,
          text: 'Time',
        },
      },
      y: {
        title: {
          display: true,
          text: getMetricLabel(metric),
        },
        beginAtZero: metric === 'engagement_score',
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  if (trendsData.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600"
        style={{ height }}
      >
        <div className="text-center">
          <div className="text-gray-400 dark:text-gray-500 text-lg mb-2">📈</div>
          <p className="text-gray-500 dark:text-gray-400">No keywords to compare</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
            Select keywords to see comparison
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default KeywordComparisonChart;