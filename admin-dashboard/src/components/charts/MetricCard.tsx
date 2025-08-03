import React from 'react';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, MinusIcon } from '@heroicons/react/24/outline';

interface MetricCardProps {
  title: string;
  value: number;
  previousValue?: number;
  format?: 'number' | 'percentage' | 'decimal';
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  previousValue,
  format = 'number',
  icon,
  trend,
  className = '',
}) => {
  const formatValue = (val: number) => {
    switch (format) {
      case 'percentage':
        return `${(val * 100).toFixed(1)}%`;
      case 'decimal':
        return val.toFixed(4);
      default:
        return val.toLocaleString();
    }
  };

  const calculateTrend = (): 'up' | 'down' | 'stable' => {
    if (trend) return trend;
    if (previousValue === undefined) return 'stable';
    
    const change = value - previousValue;
    const threshold = Math.abs(previousValue) * 0.05; // 5% threshold
    
    if (Math.abs(change) < threshold) return 'stable';
    return change > 0 ? 'up' : 'down';
  };

  const getTrendIcon = () => {
    const trendDirection = calculateTrend();
    switch (trendDirection) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />;
      default:
        return <MinusIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTrendColor = () => {
    const trendDirection = calculateTrend();
    switch (trendDirection) {
      case 'up':
        return 'text-green-600 dark:text-green-400';
      case 'down':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getChangeText = () => {
    if (previousValue === undefined) return null;
    
    const change = value - previousValue;
    const percentChange = previousValue !== 0 ? (change / previousValue) * 100 : 0;
    
    return (
      <div className={`flex items-center gap-1 text-sm ${getTrendColor()}`}>
        {getTrendIcon()}
        <span>
          {change >= 0 ? '+' : ''}{percentChange.toFixed(1)}%
        </span>
      </div>
    );
  };

  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {icon && <div className="text-gray-400">{icon}</div>}
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {title}
            </p>
          </div>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white">
            {formatValue(value)}
          </p>
          {getChangeText()}
        </div>
      </div>
    </div>
  );
};

export default MetricCard;