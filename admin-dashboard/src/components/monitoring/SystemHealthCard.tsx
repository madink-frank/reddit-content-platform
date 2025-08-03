import React from 'react';
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { SystemHealth } from '../../services/api/systemApi';

interface SystemHealthCardProps {
  health: SystemHealth;
  isLoading?: boolean;
}

const SystemHealthCard: React.FC<SystemHealthCardProps> = ({ health, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-8 w-8 text-green-500" />;
      case 'degraded':
        return <ExclamationTriangleIcon className="h-8 w-8 text-yellow-500" />;
      case 'unhealthy':
        return <XCircleIcon className="h-8 w-8 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'degraded':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'unhealthy':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getServiceStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'unhealthy':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          System Health
        </h3>
        {getStatusIcon(health.status)}
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between">
          <span className={`text-2xl font-bold ${getStatusColor(health.status)}`}>
            {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {Math.round(health.overall_health_score)}% healthy
          </span>
        </div>
        <div className="mt-2 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              health.overall_health_score >= 90
                ? 'bg-green-500'
                : health.overall_health_score >= 75
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${health.overall_health_score}%` }}
          ></div>
        </div>
      </div>

      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Services Status
        </h4>
        
        {Object.entries(health.services).map(([serviceName, serviceHealth]) => (
          <div key={serviceName} className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getServiceStatusIcon(serviceHealth.status)}
              <span className="text-sm text-gray-900 dark:text-white capitalize">
                {serviceName}
              </span>
            </div>
            <div className="text-right">
              <span className={`text-sm ${getStatusColor(serviceHealth.status)}`}>
                {serviceHealth.status}
              </span>
              {'response_time_ms' in serviceHealth && serviceHealth.response_time_ms && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {serviceHealth.response_time_ms}ms
                </div>
              )}
              {'active_workers' in serviceHealth && serviceHealth.active_workers !== undefined && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {serviceHealth.active_workers} workers
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Last updated: {new Date(health.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default SystemHealthCard;