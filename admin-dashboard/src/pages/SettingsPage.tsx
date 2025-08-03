import React, { useState } from 'react';
import { 
  UserIcon, 
  BellIcon, 
  SwatchIcon, 
  CogIcon, 
  LinkIcon 
} from '@heroicons/react/24/outline';
import {
  ProfileSettings,
  NotificationSettings,
  ThemeSettings,
  SystemSettings,
  AccountConnectionStatus,
} from '../components/settings';

type SettingsTab = 'profile' | 'notifications' | 'theme' | 'system' | 'connections';

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');

  const tabs = [
    {
      id: 'profile' as SettingsTab,
      name: 'Profile',
      icon: UserIcon,
      description: 'Manage your profile information',
    },
    {
      id: 'notifications' as SettingsTab,
      name: 'Notifications',
      icon: BellIcon,
      description: 'Configure notification preferences',
    },
    {
      id: 'theme' as SettingsTab,
      name: 'Appearance',
      icon: SwatchIcon,
      description: 'Customize theme and layout',
    },
    {
      id: 'system' as SettingsTab,
      name: 'System',
      icon: CogIcon,
      description: 'System and performance settings',
    },
    {
      id: 'connections' as SettingsTab,
      name: 'Connections',
      icon: LinkIcon,
      description: 'Account and service connections',
    },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileSettings />;
      case 'notifications':
        return <NotificationSettings />;
      case 'theme':
        return <ThemeSettings />;
      case 'system':
        return <SystemSettings />;
      case 'connections':
        return <AccountConnectionStatus />;
      default:
        return <ProfileSettings />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Settings Navigation */}
        <div className="lg:w-64 flex-shrink-0">
          <nav className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <ul className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                
                return (
                  <li key={tab.id}>
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        isActive
                          ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <Icon className={`w-4 h-4 mr-3 ${
                        isActive ? 'text-blue-500' : 'text-gray-400'
                      }`} />
                      <div className="text-left">
                        <div className="font-medium">{tab.name}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 hidden lg:block">
                          {tab.description}
                        </div>
                      </div>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>

        {/* Settings Content */}
        <div className="flex-1">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
