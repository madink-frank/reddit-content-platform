import React, { useState } from 'react';
import { useAppStore } from '../../stores/appStore';
import { useNotificationStore } from '../../stores/notificationStore';
import { 
  CogIcon, 
  ClockIcon, 
  ChartBarIcon,
  WifiIcon,
  ServerIcon,
  CircleStackIcon,
  TrashIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface SystemSettingsProps {
  className?: string;
}

interface SystemPreferences {
  autoRefresh: boolean;
  refreshInterval: number;
  enableAnalytics: boolean;
  enableRealTimeUpdates: boolean;
  maxConcurrentTasks: number;
  cacheTimeout: number;
  logLevel: 'debug' | 'info' | 'warning' | 'error';
}

const SystemSettings: React.FC<SystemSettingsProps> = ({ className = '' }) => {
  const { features, toggleFeature } = useAppStore();
  const addNotification = useNotificationStore((state) => state.addNotification);
  
  const [preferences, setPreferences] = useState<SystemPreferences>({
    autoRefresh: true,
    refreshInterval: 30,
    enableAnalytics: features.analytics,
    enableRealTimeUpdates: features.realTimeUpdates,
    maxConcurrentTasks: 5,
    cacheTimeout: 300,
    logLevel: 'info',
  });

  const [isClearing, setIsClearing] = useState(false);

  const handlePreferenceChange = <K extends keyof SystemPreferences>(
    key: K,
    value: SystemPreferences[K]
  ) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = async () => {
    try {
      // Update feature flags
      if (preferences.enableAnalytics !== features.analytics) {
        toggleFeature('analytics');
      }
      if (preferences.enableRealTimeUpdates !== features.realTimeUpdates) {
        toggleFeature('realTimeUpdates');
      }

      // TODO: Save system preferences to backend
      addNotification({
        type: 'success',
        title: 'Settings Saved',
        message: 'System settings have been updated successfully.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Save Failed',
        message: 'Failed to save system settings. Please try again.',
      });
    }
  };

  const handleClearCache = async () => {
    setIsClearing(true);
    try {
      // TODO: Implement cache clearing API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      addNotification({
        type: 'success',
        title: 'Cache Cleared',
        message: 'Application cache has been cleared successfully.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Clear Failed',
        message: 'Failed to clear cache. Please try again.',
      });
    } finally {
      setIsClearing(false);
    }
  };

  const handleResetSettings = () => {
    setPreferences({
      autoRefresh: true,
      refreshInterval: 30,
      enableAnalytics: true,
      enableRealTimeUpdates: true,
      maxConcurrentTasks: 5,
      cacheTimeout: 300,
      logLevel: 'info',
    });
    
    addNotification({
      type: 'info',
      title: 'Settings Reset',
      message: 'System settings have been reset to defaults.',
    });
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          <CogIcon className="w-5 h-5 inline mr-2" />
          System Settings
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={handleResetSettings}
            className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
          >
            Save Changes
          </button>
        </div>
      </div>

      <div className="space-y-8">
        {/* Performance Settings */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            <ChartBarIcon className="w-4 h-4 inline mr-2" />
            Performance
          </h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto Refresh Dashboard
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Automatically refresh dashboard data
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.autoRefresh}
                  onChange={(e) => handlePreferenceChange('autoRefresh', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {preferences.autoRefresh && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <ClockIcon className="w-4 h-4 inline mr-2" />
                  Refresh Interval (seconds)
                </label>
                <select
                  value={preferences.refreshInterval}
                  onChange={(e) => handlePreferenceChange('refreshInterval', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value={10}>10 seconds</option>
                  <option value={30}>30 seconds</option>
                  <option value={60}>1 minute</option>
                  <option value={300}>5 minutes</option>
                  <option value={600}>10 minutes</option>
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Concurrent Tasks
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={preferences.maxConcurrentTasks}
                onChange={(e) => handlePreferenceChange('maxConcurrentTasks', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Maximum number of background tasks to run simultaneously
              </p>
            </div>
          </div>
        </div>

        {/* Feature Toggles */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Features
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  <ChartBarIcon className="w-4 h-4 inline mr-2" />
                  Analytics Tracking
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Enable usage analytics and performance monitoring
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.enableAnalytics}
                  onChange={(e) => handlePreferenceChange('enableAnalytics', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  <WifiIcon className="w-4 h-4 inline mr-2" />
                  Real-time Updates
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Enable WebSocket connections for live data updates
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.enableRealTimeUpdates}
                  onChange={(e) => handlePreferenceChange('enableRealTimeUpdates', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Cache Settings */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            <CircleStackIcon className="w-4 h-4 inline mr-2" />
            Cache Management
          </h4>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Cache Timeout (seconds)
              </label>
              <input
                type="number"
                min="60"
                max="3600"
                value={preferences.cacheTimeout}
                onChange={(e) => handlePreferenceChange('cacheTimeout', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                How long to cache API responses before refreshing
              </p>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div>
                <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                  Clear Application Cache
                </h5>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Remove all cached data to free up space and refresh content
                </p>
              </div>
              <button
                onClick={handleClearCache}
                disabled={isClearing}
                className="flex items-center px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50"
              >
                {isClearing ? (
                  <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <TrashIcon className="w-4 h-4 mr-2" />
                )}
                {isClearing ? 'Clearing...' : 'Clear Cache'}
              </button>
            </div>
          </div>
        </div>

        {/* Logging Settings */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            <ServerIcon className="w-4 h-4 inline mr-2" />
            Logging
          </h4>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Log Level
            </label>
            <select
              value={preferences.logLevel}
              onChange={(e) => handlePreferenceChange('logLevel', e.target.value as SystemPreferences['logLevel'])}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="debug">Debug (Most Verbose)</option>
              <option value="info">Info (Recommended)</option>
              <option value="warning">Warning</option>
              <option value="error">Error (Least Verbose)</option>
            </select>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Controls the amount of logging information displayed in the console
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemSettings;