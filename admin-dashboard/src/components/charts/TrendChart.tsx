import React, { useState, useEffect } from 'react';
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
import { TrendMetrics } from '../../types';
import ResponsiveChartContainer from './ResponsiveChartContainer';

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

interface TrendChartProps {
  data: TrendMetrics[];
  title?: string;
  height?: number;
  showEngagement?: boolean;
  showTfIdf?: boolean;
  showVelocity?: boolean;
}

const TrendChart: React.FC<TrendChartProps> = ({
  data,
  title = 'Trend Analysis',
  height = 400,
  showEngagement = true,
  showTfIdf = true,
  showVelocity = true,
}) => {
  const [chartOptions, setChartOptions] = useState({
    showEngagement,
    showTfIdf,
    showVelocity,
  });
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 640);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const handleToggleOption = (key: string, enabled: boolean) => {
    setChartOptions(prev => ({
      ...prev,
      [key]: enabled,
    }));
  };
  const chartData = {
    labels: data.map((item) => new Date(item.calculated_at)),
    datasets: [
      ...(chartOptions.showEngagement
        ? [
            {
              label: 'Engagement Score',
              data: data.map((item) => item.engagement_score),
              borderColor: 'rgb(59, 130, 246)',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              borderWidth: isMobile ? 1.5 : 2,
              fill: false,
              tension: 0.4,
              yAxisID: 'y',
              pointRadius: isMobile ? 2 : 3,
              pointHoverRadius: isMobile ? 4 : 6,
            },
          ]
        : []),
      ...(chartOptions.showTfIdf
        ? [
            {
              label: 'TF-IDF Score',
              data: data.map((item) => item.tfidf_score),
              borderColor: 'rgb(16, 185, 129)',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderWidth: isMobile ? 1.5 : 2,
              fill: false,
              tension: 0.4,
              yAxisID: 'y1',
              pointRadius: isMobile ? 2 : 3,
              pointHoverRadius: isMobile ? 4 : 6,
            },
          ]
        : []),
      ...(chartOptions.showVelocity
        ? [
            {
              label: 'Trend Velocity',
              data: data.map((item) => item.trend_velocity),
              borderColor: 'rgb(245, 101, 101)',
              backgroundColor: 'rgba(245, 101, 101, 0.1)',
              borderWidth: isMobile ? 1.5 : 2,
              fill: false,
              tension: 0.4,
              yAxisID: 'y2',
              pointRadius: isMobile ? 2 : 3,
              pointHoverRadius: isMobile ? 4 : 6,
            },
          ]
        : []),
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: isMobile ? 'bottom' as const : 'top' as const,
        labels: {
          usePointStyle: true,
          padding: isMobile ? 10 : 20,
          font: {
            size: isMobile ? 10 : 12,
          },
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
            hour: isMobile ? 'HH:mm' : 'MMM dd HH:mm',
            day: isMobile ? 'dd' : 'MMM dd',
            week: isMobile ? 'dd' : 'MMM dd',
            month: isMobile ? 'MMM' : 'MMM yyyy',
          },
        },
        title: {
          display: !isMobile,
          text: 'Time',
          font: {
            size: isMobile ? 10 : 12,
          },
        },
        ticks: {
          font: {
            size: isMobile ? 9 : 11,
          },
          maxTicksLimit: isMobile ? 4 : 8,
        },
      },
      y: {
        type: 'linear' as const,
        display: chartOptions.showEngagement,
        position: 'left' as const,
        title: {
          display: !isMobile,
          text: 'Engagement Score',
          color: 'rgb(59, 130, 246)',
          font: {
            size: isMobile ? 10 : 12,
          },
        },
        grid: {
          drawOnChartArea: true,
        },
        ticks: {
          font: {
            size: isMobile ? 9 : 11,
          },
        },
      },
      y1: {
        type: 'linear' as const,
        display: chartOptions.showTfIdf && !isMobile,
        position: 'right' as const,
        title: {
          display: !isMobile,
          text: 'TF-IDF Score',
          color: 'rgb(16, 185, 129)',
          font: {
            size: isMobile ? 10 : 12,
          },
        },
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          font: {
            size: isMobile ? 9 : 11,
          },
        },
      },
      y2: {
        type: 'linear' as const,
        display: chartOptions.showVelocity && !chartOptions.showTfIdf && !isMobile,
        position: 'right' as const,
        title: {
          display: !isMobile,
          text: 'Trend Velocity',
          color: 'rgb(245, 101, 101)',
          font: {
            size: isMobile ? 10 : 12,
          },
        },
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          font: {
            size: isMobile ? 9 : 11,
          },
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  const toggleOptions = [
    {
      label: 'Engagement',
      key: 'showEngagement',
      enabled: chartOptions.showEngagement,
      onChange: handleToggleOption,
    },
    {
      label: 'TF-IDF',
      key: 'showTfIdf',
      enabled: chartOptions.showTfIdf,
      onChange: handleToggleOption,
    },
    {
      label: 'Velocity',
      key: 'showVelocity',
      enabled: chartOptions.showVelocity,
      onChange: handleToggleOption,
    },
  ];

  if (data.length === 0) {
    return (
      <ResponsiveChartContainer
        title={title}
        height={{ mobile: 250, tablet: 350, desktop: height }}
      >
        <div className="flex items-center justify-center h-full bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
          <div className="text-center">
            <div className="text-gray-400 dark:text-gray-500 text-lg mb-2">📊</div>
            <p className="text-gray-500 dark:text-gray-400">No trend data available</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Run trend analysis to see charts
            </p>
          </div>
        </div>
      </ResponsiveChartContainer>
    );
  }

  return (
    <ResponsiveChartContainer
      title={title}
      showToggleOptions={true}
      toggleOptions={toggleOptions}
      height={{ mobile: 300, tablet: 400, desktop: height }}
    >
      <Line data={chartData} options={options} />
    </ResponsiveChartContainer>
  );
};

export default TrendChart;