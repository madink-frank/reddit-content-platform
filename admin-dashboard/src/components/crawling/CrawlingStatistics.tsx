import React, { useState } from 'react';
import { 
  ChartBarIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  ClockIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { useCrawlStatistics } from '../../hooks/useCrawling';
import LoadingSpinner from '../ui/LoadingSpinner';

const CrawlingStatistics: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState(7);
  const { data: statsResponse, isLoading, error } = useCrawlStatistics(selectedPeriod);

  const stats = statsResponse?.data;

  const periodOptions = [
    { value: 1, label: 'Last 24 hours' },
    { value: 7, label: 'Last 7 days' },
    { value: 30, label: 'Last 30 days' },
    { value: 90, label: 'Last 90 days' },
  ];

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
    percentage?: number;
  }> = ({ title, value, icon, color, percentage }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 ${color}`}>
          {icon}
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
              {title}
            </dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                {value.toLocaleString()}
              </div>
              {percentage !== undefined && (
                <div className="ml-2 flex items-baseline text-sm font-semibold">
                  <span className={percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-center">
          <LoadingSpinner />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading statistics...</span>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="text-center text-red-600 dark:text-red-400">
          <ExclamationCircleIcon className="h-8 w-8 mx-auto mb-2" />
          <p>Failed to load crawling statistics</p>
        </div>
      </div>
    );
  }

  const crawlingStats = stats.crawling_tasks;

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Crawling Statistics
          </h2>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          >
            {periodOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <StatCard
            title="Total Tasks"
            value={crawlingStats.total}
            icon={<ChartBarIcon className="h-6 w-6" />}
            color="text-blue-600"
          />
          <StatCard
            title="Completed"
            value={crawlingStats.completed}
            icon={<CheckCircleIcon className="h-6 w-6" />}
            color="text-green-600"
          />
          <StatCard
            title="Failed"
            value={crawlingStats.failed}
            icon={<ExclamationCircleIcon className="h-6 w-6" />}
            color="text-red-600"
          />
          <StatCard
            title="Running"
            value={crawlingStats.running}
            icon={<ClockIcon className="h-6 w-6" />}
            color="text-yellow-600"
          />
        </div>

        {/* Success Rate */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Success Rate
            </span>
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              {crawlingStats.success_rate.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${crawlingStats.success_rate}%` }}
            />
          </div>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Task Status Breakdown
        </h3>
        
        <div className="space-y-4">
          {[
            { 
              status: 'completed', 
              count: crawlingStats.completed, 
              color: 'bg-green-500', 
              icon: <CheckCircleIcon className="h-5 w-5 text-green-600" />,
              label: 'Completed'
            },
            { 
              status: 'running', 
              count: crawlingStats.running, 
              color: 'bg-blue-500', 
              icon: <ClockIcon className="h-5 w-5 text-blue-600" />,
              label: 'Running'
            },
            { 
              status: 'pending', 
              count: crawlingStats.pending, 
              color: 'bg-yellow-500', 
              icon: <ClockIcon className="h-5 w-5 text-yellow-600" />,
              label: 'Pending'
            },
            { 
              status: 'failed', 
              count: crawlingStats.failed, 
              color: 'bg-red-500', 
              icon: <ExclamationCircleIcon className="h-5 w-5 text-red-600" />,
              label: 'Failed'
            },
            { 
              status: 'cancelled', 
              count: crawlingStats.cancelled, 
              color: 'bg-gray-500', 
              icon: <XCircleIcon className="h-5 w-5 text-gray-600" />,
              label: 'Cancelled'
            },
          ].map((item) => {
            const percentage = crawlingStats.total > 0 ? (item.count / crawlingStats.total) * 100 : 0;
            
            return (
              <div key={item.status} className="flex items-center">
                <div className="flex items-center space-x-3 flex-1">
                  {item.icon}
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {item.label}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-32 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div
                      className={`${item.color} h-2 rounded-full transition-all duration-300`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">
                    {item.count}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 w-12 text-right">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Overall System Stats */}
      {stats.overall_stats && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Overall System Statistics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.overall_stats.total_tasks}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Tasks</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {stats.overall_stats.success_rate.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Overall Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Object.keys(stats.overall_stats.by_type).length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Task Types</div>
            </div>
          </div>

          {/* Task Types Breakdown */}
          {Object.keys(stats.overall_stats.by_type).length > 1 && (
            <div className="mt-6">
              <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">
                By Task Type
              </h4>
              <div className="space-y-2">
                {Object.entries(stats.overall_stats.by_type).map(([type, typeStats]: [string, any]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                      {type}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {typeStats.completed}/{typeStats.total}
                      </span>
                      <div className="w-20 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ 
                            width: `${typeStats.total > 0 ? (typeStats.completed / typeStats.total) * 100 : 0}%` 
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CrawlingStatistics;