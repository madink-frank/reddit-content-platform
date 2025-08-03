import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';


ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TfIdfChartProps {
  data: Array<{
    keyword: string;
    tfidf_score: number;
    post_count: number;
  }>;
  title?: string;
  height?: number;
  maxItems?: number;
}

const TfIdfChart: React.FC<TfIdfChartProps> = ({
  data,
  title = 'TF-IDF Scores by Keyword',
  height = 400,
  maxItems = 10,
}) => {
  // Sort by TF-IDF score and take top items
  const sortedData = [...data]
    .sort((a, b) => b.tfidf_score - a.tfidf_score)
    .slice(0, maxItems);

  const chartData = {
    labels: sortedData.map((item) => item.keyword),
    datasets: [
      {
        label: 'TF-IDF Score',
        data: sortedData.map((item) => item.tfidf_score),
        backgroundColor: sortedData.map((_, index) => {
          const opacity = 0.8 - (index * 0.05);
          return `rgba(59, 130, 246, ${Math.max(opacity, 0.3)})`;
        }),
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
        padding: {
          bottom: 20,
        },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const dataIndex = context.dataIndex;
            const item = sortedData[dataIndex];
            return [
              `TF-IDF Score: ${context.parsed.y.toFixed(4)}`,
              `Posts: ${item.post_count}`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Keywords',
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0,
        },
      },
      y: {
        title: {
          display: true,
          text: 'TF-IDF Score',
        },
        beginAtZero: true,
      },
    },
  };

  if (data.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600"
        style={{ height }}
      >
        <div className="text-center">
          <div className="text-gray-400 dark:text-gray-500 text-lg mb-2">📊</div>
          <p className="text-gray-500 dark:text-gray-400">No TF-IDF data available</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
            Run trend analysis to see TF-IDF scores
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default TfIdfChart;