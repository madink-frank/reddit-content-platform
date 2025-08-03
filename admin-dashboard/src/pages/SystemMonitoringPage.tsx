import React, { useState } from 'react';
import {
  CpuChipIcon,
  ServerIcon,
  ClockIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import { useSystemHealthDetailed, useSystemMetrics, useSystemAlerts } from '../hooks/useSystem';
import SystemHealthCard from '../components/monitoring/SystemHealthCard';
import SystemMetricsChart from '../components/monitoring/SystemMetricsChart';
import ApiPerformanceChart from '../components/monitoring/ApiPerformanceChart';
import SystemAlerts from '../components/monitoring/SystemAlerts';
import MetricCard from '../components/monitoring/MetricCard';

const SystemMonitoringPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('1h');
  const [refreshInterval, setRefreshInterval] = useState(30);

  // Fetch data
  const { data: systemHealth, isLoading: healthLoading } = useSystemHealthDetailed();
  const { data: metrics, isLoading: metricsLoading } = useSystemMetrics({ time_range: timeRange });
  const { data: alerts, isLoading: alertsLoading } = useSystemAlerts({ resolved: false });

  // Get current metrics for cards
  const currentMetrics = metrics && metrics.length > 0 ? metrics[metrics.length - 1] : null;

  const timeRangeOptions = [
    { value: '1h', label: '1 Hour' },
    { value: '6h', label: '6 Hours' },
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
  ];

  const refreshOptions = [
    { value: 10, label: '10s' },
    { value: 30, label: '30s' },
    { value: 60, label: '1m' },
    { value: 300, label: '5m' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            System Monitoring
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time system health and performance metrics
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Time Range Selector */}
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600 dark:text-gray-400">
              Time Range:
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {timeRangeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Refresh Interval Selector */}
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600 dark:text-gray-400">
              Refresh:
            </label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {refreshOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="API Requests"
          value={currentMetrics?.api_requests_total || 0}
          icon={<ChartBarIcon className="h-6 w-6" />}
          color="blue"
          isLoading={metricsLoading}
        />
        <MetricCard
          title="Response Time"
          value={currentMetrics ? Math.round(currentMetrics.api_response_time_avg * 1000) : 0}
          unit="ms"
          icon={<ClockIcon className="h-6 w-6" />}
          color="green"
          isLoading={metricsLoading}
        />
        <MetricCard
          title="Active Tasks"
          value={currentMetrics?.active_tasks || 0}
          icon={<Cog6ToothIcon className="h-6 w-6" />}
          color="purple"
          isLoading={metricsLoading}
        />
        <MetricCard
          title="CPU Usage"
          value={currentMetrics ? Math.round(currentMetrics.system_cpu_usage) : 0}
          unit="%"
          icon={<CpuChipIcon className="h-6 w-6" />}
          color={currentMetrics && currentMetrics.system_cpu_usage > 80 ? 'red' : 'yellow'}
          isLoading={metricsLoading}
        />
      </div>

      {/* System Health and Alerts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <SystemHealthCard 
          health={systemHealth!} 
          isLoading={healthLoading} 
        />

        {/* System Alerts */}
        <SystemAlerts 
          alerts={alerts || []} 
          isLoading={alertsLoading}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* System Metrics Chart */}
        <SystemMetricsChart
          metrics={metrics || []}
          isLoading={metricsLoading}
          timeRange={timeRange}
        />

        {/* API Performance Chart */}
        <ApiPerformanceChart
          metrics={metrics || []}
          isLoading={metricsLoading}
        />
      </div>

      {/* Additional Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Memory Usage"
          value={currentMetrics ? Math.round(currentMetrics.system_memory_usage) : 0}
          unit="%"
          icon={<ServerIcon className="h-6 w-6" />}
          color={currentMetrics && currentMetrics.system_memory_usage > 85 ? 'red' : 'blue'}
          isLoading={metricsLoading}
        />
        <MetricCard
          title="Disk Usage"
          value={currentMetrics ? Math.round(currentMetrics.system_disk_usage) : 0}
          unit="%"
          icon={<ServerIcon className="h-6 w-6" />}
          color={currentMetrics && currentMetrics.system_disk_usage > 90 ? 'red' : 'green'}
          isLoading={metricsLoading}
        />
        <MetricCard
          title="DB Connections"
          value={currentMetrics?.database_connections || 0}
          icon={<ServerIcon className="h-6 w-6" />}
          color="purple"
          isLoading={metricsLoading}
        />
        <MetricCard
          title="Crawling Success"
          value={currentMetrics ? Math.round(currentMetrics.crawling_success_rate) : 0}
          unit="%"
          icon={<ChartBarIcon className="h-6 w-6" />}
          color={currentMetrics && currentMetrics.crawling_success_rate < 80 ? 'red' : 'green'}
          isLoading={metricsLoading}
        />
      </div>

      {/* Status Footer */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
            <span>•</span>
            <span>Auto-refresh: {refreshInterval}s</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live monitoring active</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitoringPage;