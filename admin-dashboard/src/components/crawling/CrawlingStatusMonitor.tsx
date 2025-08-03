import React from 'react';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  ClockIcon, 
  PlayIcon,
  XCircleIcon,
  StopIcon
} from '@heroicons/react/24/outline';
import { useCrawlStatus, useCancelCrawlTask } from '../../hooks/useCrawling';
import { CrawlTaskInfo } from '../../services/api/crawlingApi';
import LoadingSpinner from '../ui/LoadingSpinner';

const CrawlingStatusMonitor: React.FC = () => {
  const { data: statusResponse, isLoading, error } = useCrawlStatus(20);
  const cancelTask = useCancelCrawlTask();

  const tasks = statusResponse?.data?.tasks || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      case 'running':
        return <PlayIcon className="h-5 w-5 text-blue-500" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'cancelled':
        return <XCircleIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/20';
      case 'failed':
        return 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-900/20';
      case 'running':
        return 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/20';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 dark:text-yellow-400 dark:bg-yellow-900/20';
      case 'cancelled':
        return 'text-gray-600 bg-gray-50 dark:text-gray-400 dark:bg-gray-900/20';
      default:
        return 'text-gray-600 bg-gray-50 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (startDate: string, endDate?: string) => {
    const start = new Date(startDate);
    const end = endDate ? new Date(endDate) : new Date();
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  const handleCancelTask = (taskId: string) => {
    if (window.confirm('Are you sure you want to cancel this task?')) {
      cancelTask.mutate(taskId);
    }
  };

  const renderProgressBar = (task: CrawlTaskInfo) => {
    if (task.status !== 'running' || typeof task.progress !== 'number') {
      return null;
    }

    return (
      <div className="mt-2">
        <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
          <span>Progress</span>
          <span>{Math.round(task.progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${task.progress}%` }}
          />
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-center">
          <LoadingSpinner />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading crawling status...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="text-center text-red-600 dark:text-red-400">
          <ExclamationCircleIcon className="h-8 w-8 mx-auto mb-2" />
          <p>Failed to load crawling status</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Crawling Status Monitor
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Real-time status of crawling tasks
        </p>
      </div>

      <div className="p-6">
        {tasks.length === 0 ? (
          <div className="text-center py-8">
            <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">No crawling tasks found</p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Start a crawling task to see its status here
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    {getStatusIcon(task.status)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}
                        >
                          {task.status.toUpperCase()}
                        </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          Task #{task.id}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <div>
                          <span className="font-medium">Task ID:</span> {task.task_id}
                        </div>
                        
                        {task.metadata?.keyword && (
                          <div>
                            <span className="font-medium">Keyword:</span> {task.metadata.keyword}
                          </div>
                        )}
                        
                        {task.metadata?.subreddit && (
                          <div>
                            <span className="font-medium">Subreddit:</span> r/{task.metadata.subreddit}
                          </div>
                        )}
                        
                        {task.metadata?.limit && (
                          <div>
                            <span className="font-medium">Limit:</span> {task.metadata.limit} posts
                          </div>
                        )}
                        
                        <div>
                          <span className="font-medium">Started:</span> {formatDate(task.created_at)}
                        </div>
                        
                        {task.completed_at && (
                          <div>
                            <span className="font-medium">Completed:</span> {formatDate(task.completed_at)}
                          </div>
                        )}
                        
                        <div>
                          <span className="font-medium">Duration:</span> {formatDuration(task.created_at, task.completed_at)}
                        </div>
                        
                        {task.error_message && (
                          <div className="text-red-600 dark:text-red-400">
                            <span className="font-medium">Error:</span> {task.error_message}
                          </div>
                        )}
                      </div>

                      {renderProgressBar(task)}

                      {task.result && task.status === 'completed' && (
                        <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-md">
                          <div className="text-sm text-green-800 dark:text-green-200">
                            <div className="font-medium mb-1">Results:</div>
                            {typeof task.result === 'object' ? (
                              <div className="space-y-1">
                                {task.result.posts_collected && (
                                  <div>Posts collected: {task.result.posts_collected}</div>
                                )}
                                {task.result.comments_collected && (
                                  <div>Comments collected: {task.result.comments_collected}</div>
                                )}
                                {task.result.processing_time && (
                                  <div>Processing time: {task.result.processing_time}s</div>
                                )}
                              </div>
                            ) : (
                              <div>{String(task.result)}</div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {(task.status === 'running' || task.status === 'pending') && (
                    <button
                      onClick={() => handleCancelTask(task.task_id)}
                      disabled={cancelTask.isPending}
                      className="ml-4 inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30"
                    >
                      <StopIcon className="h-3 w-3 mr-1" />
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CrawlingStatusMonitor;