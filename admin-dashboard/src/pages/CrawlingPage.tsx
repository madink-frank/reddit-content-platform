import React, { useState } from 'react';
import { Cog6ToothIcon } from '@heroicons/react/24/outline';
import CrawlingControlPanel from '../components/crawling/CrawlingControlPanel';
import CrawlingStatusMonitor from '../components/crawling/CrawlingStatusMonitor';
import CrawlingStatistics from '../components/crawling/CrawlingStatistics';

const CrawlingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'control' | 'status' | 'statistics'>('control');
  const [showSettings, setShowSettings] = useState(false);

  const tabs = [
    { id: 'control' as const, name: 'Control Panel', description: 'Start and configure crawling tasks' },
    { id: 'status' as const, name: 'Status Monitor', description: 'Real-time task monitoring' },
    { id: 'statistics' as const, name: 'Statistics', description: 'Performance metrics and analytics' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Crawling Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage Reddit content crawling tasks and monitor their progress
          </p>
        </div>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Cog6ToothIcon className="h-4 w-4 mr-2" />
          Settings
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <div className="flex flex-col items-start">
                <span>{tab.name}</span>
                <span className="text-xs text-gray-400 dark:text-gray-500 font-normal">
                  {tab.description}
                </span>
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <Cog6ToothIcon className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Crawling Settings
              </h3>
              <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                <p>Advanced crawling settings and scheduling options will be available here.</p>
                <p className="mt-1">This feature is planned for a future update.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'control' && (
          <CrawlingControlPanel onSettingsClick={() => setShowSettings(!showSettings)} />
        )}
        
        {activeTab === 'status' && <CrawlingStatusMonitor />}
        
        {activeTab === 'statistics' && <CrawlingStatistics />}
      </div>
    </div>
  );
};

export default CrawlingPage;
