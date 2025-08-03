import React, { useState, useEffect } from 'react';
import { useGenerationStatus } from '../../hooks/useContent';
// ContentGenerationStatus type is used in props interface
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface ContentGenerationMonitorProps {
  taskId: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

export const ContentGenerationMonitor: React.FC<ContentGenerationMonitorProps> = ({
  taskId,
  onComplete,
  onError
}) => {
  const { data: status, isLoading } = useGenerationStatus(taskId, !!taskId);
  const [previousStatus, setPreviousStatus] = useState<string>('');

  useEffect(() => {
    if (status && status.status !== previousStatus) {
      setPreviousStatus(status.status);
      
      if (status.status === 'completed' && status.result) {
        onComplete?.(status.result);
      } else if (status.status === 'failed' && status.error) {
        onError?.(status.error);
      }
    }
  }, [status, previousStatus, onComplete, onError]);

  if (isLoading || !status) {
    return (
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-center">
          <ArrowPathIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin mr-3" />
          <div>
            <p className="text-blue-800 dark:text-blue-200 font-medium">
              Initializing content generation...
            </p>
            <p className="text-blue-600 dark:text-blue-400 text-sm">
              Task ID: {taskId}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400" />;
      case 'failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-600 dark:text-red-400" />;
      case 'running':
        return <ArrowPathIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'failed':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'running':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
      default:
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'completed':
        return 'Content generation completed successfully!';
      case 'failed':
        return 'Content generation failed';
      case 'running':
        return 'Generating content...';
      case 'pending':
        return 'Content generation queued';
      default:
        return 'Unknown status';
    }
  };

  const getTextColor = () => {
    switch (status.status) {
      case 'completed':
        return 'text-green-800 dark:text-green-200';
      case 'failed':
        return 'text-red-800 dark:text-red-200';
      case 'running':
        return 'text-blue-800 dark:text-blue-200';
      default:
        return 'text-yellow-800 dark:text-yellow-200';
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor()}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0 mr-3 mt-0.5">
          {getStatusIcon()}
        </div>
        <div className="flex-1">
          <p className={`font-medium ${getTextColor()}`}>
            {getStatusText()}
          </p>
          
          {status.message && (
            <p className={`text-sm mt-1 ${getTextColor().replace('800', '600').replace('200', '300')}`}>
              {status.message}
            </p>
          )}

          {status.progress > 0 && status.status === 'running' && (
            <div className="mt-3">
              <div className="flex justify-between text-sm mb-1">
                <span className={getTextColor().replace('800', '600').replace('200', '300')}>
                  Progress
                </span>
                <span className={getTextColor().replace('800', '600').replace('200', '300')}>
                  {status.progress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${status.progress}%` }}
                />
              </div>
            </div>
          )}

          {status.error && status.status === 'failed' && (
            <div className="mt-3 p-3 bg-red-100 dark:bg-red-900/30 rounded border border-red-200 dark:border-red-800">
              <p className="text-red-800 dark:text-red-200 text-sm font-medium">
                Error Details:
              </p>
              <p className="text-red-700 dark:text-red-300 text-sm mt-1">
                {status.error}
              </p>
            </div>
          )}

          <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 space-y-1">
            <div>Task ID: {status.task_id}</div>
            <div>Started: {new Date(status.created_at).toLocaleString()}</div>
            {status.completed_at && (
              <div>Completed: {new Date(status.completed_at).toLocaleString()}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};