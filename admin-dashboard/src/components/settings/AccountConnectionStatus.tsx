import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotificationStore } from '../../stores/notificationStore';
import { 
  LinkIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  XCircleIcon,
  ArrowPathIcon,
  ClockIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

interface AccountConnectionStatusProps {
  className?: string;
}

interface ConnectionStatus {
  service: string;
  status: 'connected' | 'disconnected' | 'error' | 'checking';
  lastChecked: Date;
  error?: string;
  details?: {
    username?: string;
    permissions?: string[];
    expiresAt?: Date;
  };
}

const AccountConnectionStatus: React.FC<AccountConnectionStatusProps> = ({ className = '' }) => {
  const { user, tokens } = useAuth();
  const addNotification = useNotificationStore((state) => state.addNotification);
  
  const [connections, setConnections] = useState<ConnectionStatus[]>([
    {
      service: 'Reddit',
      status: user ? 'connected' : 'disconnected',
      lastChecked: new Date(),
      details: user ? {
        username: user.name,
        permissions: ['identity', 'read'],
        expiresAt: tokens ? new Date(Date.now() + tokens.expires_in * 1000) : undefined,
      } : undefined,
    },
    {
      service: 'Database',
      status: 'connected',
      lastChecked: new Date(),
    },
    {
      service: 'Redis Cache',
      status: 'connected',
      lastChecked: new Date(),
    },
    {
      service: 'Background Tasks',
      status: 'connected',
      lastChecked: new Date(),
    },
  ]);

  const [isRefreshing, setIsRefreshing] = useState(false);

  const checkConnectionStatus = async (service: string) => {
    setConnections(prev => prev.map(conn => 
      conn.service === service 
        ? { ...conn, status: 'checking' }
        : conn
    ));

    try {
      // TODO: Implement actual connection checks
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      setConnections(prev => prev.map(conn => 
        conn.service === service 
          ? { ...conn, status: 'connected', lastChecked: new Date() }
          : conn
      ));
    } catch (error) {
      setConnections(prev => prev.map(conn => 
        conn.service === service 
          ? { 
              ...conn, 
              status: 'error', 
              lastChecked: new Date(),
              error: 'Connection check failed'
            }
          : conn
      ));
    }
  };

  const refreshAllConnections = async () => {
    setIsRefreshing(true);
    try {
      // Check all connections
      await Promise.all(
        connections.map(conn => checkConnectionStatus(conn.service))
      );
      
      addNotification({
        type: 'success',
        title: 'Connections Refreshed',
        message: 'All connection statuses have been updated.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Refresh Failed',
        message: 'Failed to refresh connection statuses.',
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusIcon = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'disconnected':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'checking':
        return <ArrowPathIcon className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <XCircleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'error':
        return 'Error';
      case 'checking':
        return 'Checking...';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'connected':
        return 'text-green-600 dark:text-green-400';
      case 'disconnected':
        return 'text-red-600 dark:text-red-400';
      case 'error':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'checking':
        return 'text-blue-600 dark:text-blue-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  // Auto-refresh connections every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      refreshAllConnections();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          <LinkIcon className="w-5 h-5 inline mr-2" />
          Account & Service Connections
        </h3>
        <button
          onClick={refreshAllConnections}
          disabled={isRefreshing}
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-50"
        >
          <ArrowPathIcon className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Refreshing...' : 'Refresh All'}
        </button>
      </div>

      <div className="space-y-4">
        {connections.map((connection) => (
          <div
            key={connection.service}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                {getStatusIcon(connection.status)}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    {connection.service}
                  </h4>
                  <p className={`text-xs ${getStatusColor(connection.status)}`}>
                    {getStatusText(connection.status)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  <ClockIcon className="w-3 h-3 inline mr-1" />
                  {formatTimeAgo(connection.lastChecked)}
                </p>
                {connection.status !== 'checking' && (
                  <button
                    onClick={() => checkConnectionStatus(connection.service)}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 mt-1"
                  >
                    Check Now
                  </button>
                )}
              </div>
            </div>

            {/* Connection Details */}
            {connection.details && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="grid grid-cols-1 gap-2 text-xs">
                  {connection.details.username && (
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Username:</span>
                      <span className="text-gray-900 dark:text-white">{connection.details.username}</span>
                    </div>
                  )}
                  {connection.details.permissions && (
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Permissions:</span>
                      <span className="text-gray-900 dark:text-white">
                        {connection.details.permissions.join(', ')}
                      </span>
                    </div>
                  )}
                  {connection.details.expiresAt && (
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Expires:</span>
                      <span className="text-gray-900 dark:text-white">
                        {connection.details.expiresAt.toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error Message */}
            {connection.error && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-red-600 dark:text-red-400">
                  <ExclamationTriangleIcon className="w-3 h-3 inline mr-1" />
                  {connection.error}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Overall Status Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <GlobeAltIcon className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Overall System Status:
            </span>
          </div>
          <div className="flex items-center space-x-2">
            {connections.every(conn => conn.status === 'connected') ? (
              <>
                <CheckCircleIcon className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-600 dark:text-green-400">All Systems Operational</span>
              </>
            ) : connections.some(conn => conn.status === 'error') ? (
              <>
                <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" />
                <span className="text-sm text-yellow-600 dark:text-yellow-400">Some Issues Detected</span>
              </>
            ) : (
              <>
                <XCircleIcon className="w-4 h-4 text-red-500" />
                <span className="text-sm text-red-600 dark:text-red-400">Service Disruption</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountConnectionStatus;