import React, { useState } from 'react';
import { useNotificationStore } from '../../stores/notificationStore';
import { useAppStore } from '../../stores/appStore';
import { 
  BellIcon, 
  EnvelopeIcon, 
  ComputerDesktopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface NotificationSettingsProps {
  className?: string;
}

interface NotificationPreferences {
  email: {
    crawlingComplete: boolean;
    contentGenerated: boolean;
    systemAlerts: boolean;
    weeklyReport: boolean;
  };
  browser: {
    crawlingComplete: boolean;
    contentGenerated: boolean;
    systemAlerts: boolean;
    realTimeUpdates: boolean;
  };
  types: {
    success: boolean;
    error: boolean;
    warning: boolean;
    info: boolean;
  };
}

const NotificationSettings: React.FC<NotificationSettingsProps> = ({ className = '' }) => {
  const addNotification = useNotificationStore((state) => state.addNotification);
  const { features, toggleFeature } = useAppStore();
  
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email: {
      crawlingComplete: true,
      contentGenerated: true,
      systemAlerts: true,
      weeklyReport: false,
    },
    browser: {
      crawlingComplete: true,
      contentGenerated: true,
      systemAlerts: true,
      realTimeUpdates: features.realTimeUpdates,
    },
    types: {
      success: true,
      error: true,
      warning: true,
      info: true,
    },
  });

  const handlePreferenceChange = (
    category: keyof NotificationPreferences,
    key: string,
    value: boolean
  ) => {
    setPreferences(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value,
      },
    }));
  };

  const handleSave = async () => {
    try {
      // Update real-time updates feature flag
      if (preferences.browser.realTimeUpdates !== features.realTimeUpdates) {
        toggleFeature('realTimeUpdates');
      }

      // TODO: Save notification preferences to backend
      addNotification({
        type: 'success',
        title: 'Settings Saved',
        message: 'Your notification preferences have been updated.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Save Failed',
        message: 'Failed to save notification settings. Please try again.',
      });
    }
  };

  const testNotification = (type: 'success' | 'error' | 'warning' | 'info') => {
    const messages = {
      success: { title: 'Test Success', message: 'This is a test success notification.' },
      error: { title: 'Test Error', message: 'This is a test error notification.' },
      warning: { title: 'Test Warning', message: 'This is a test warning notification.' },
      info: { title: 'Test Info', message: 'This is a test info notification.' },
    };

    addNotification({
      type,
      ...messages[type],
    });
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          <BellIcon className="w-5 h-5 inline mr-2" />
          Notification Settings
        </h3>
        <button
          onClick={handleSave}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
        >
          Save Changes
        </button>
      </div>

      <div className="space-y-8">
        {/* Email Notifications */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            <EnvelopeIcon className="w-4 h-4 inline mr-2" />
            Email Notifications
          </h4>
          <div className="space-y-3">
            {Object.entries(preferences.email).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {getNotificationDescription(key)}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => handlePreferenceChange('email', key, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Browser Notifications */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            <ComputerDesktopIcon className="w-4 h-4 inline mr-2" />
            Browser Notifications
          </h4>
          <div className="space-y-3">
            {Object.entries(preferences.browser).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {getNotificationDescription(key)}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => handlePreferenceChange('browser', key, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Notification Types */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Notification Types
          </h4>
          <div className="space-y-3">
            {Object.entries(preferences.types).map(([key, value]) => {
              const icons = {
                success: CheckCircleIcon,
                error: XCircleIcon,
                warning: ExclamationTriangleIcon,
                info: InformationCircleIcon,
              };
              const Icon = icons[key as keyof typeof icons];
              
              return (
                <div key={key} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${getTypeColor(key)}`} />
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                        {key} Notifications
                      </label>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Show {key} notifications in the app
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => testNotification(key as any)}
                      className="px-2 py-1 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                    >
                      Test
                    </button>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => handlePreferenceChange('types', key, e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Global Notification Settings */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Global Settings
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Enable All Notifications
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Master switch for all notification types
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={features.notifications}
                  onChange={() => toggleFeature('notifications')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const getNotificationDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    crawlingComplete: 'Notify when Reddit crawling tasks finish',
    contentGenerated: 'Notify when blog content is generated',
    systemAlerts: 'Notify about system errors and warnings',
    weeklyReport: 'Send weekly summary reports',
    realTimeUpdates: 'Enable real-time dashboard updates',
  };
  return descriptions[key] || 'Notification setting';
};

const getTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500',
  };
  return colors[type] || 'text-gray-500';
};

export default NotificationSettings;