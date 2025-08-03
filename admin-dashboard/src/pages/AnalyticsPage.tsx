import React, { useState } from 'react';
import { FunnelIcon } from '@heroicons/react/24/outline';
import TrendMetricsDashboard from '../components/charts/TrendMetricsDashboard';
import { useKeywords } from '../hooks/useKeywords';

const AnalyticsPage: React.FC = () => {
  const [selectedKeywords, setSelectedKeywords] = useState<number[]>([]);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d' | '30d'>('24h');
  const [showFilters, setShowFilters] = useState(false);

  const { data: keywords } = useKeywords();

  const handleKeywordToggle = (keywordId: number) => {
    setSelectedKeywords(prev => 
      prev.includes(keywordId)
        ? prev.filter(id => id !== keywordId)
        : [...prev, keywordId]
    );
  };

  const handleSelectAll = () => {
    if (keywords?.keywords) {
      setSelectedKeywords(keywords.keywords.map(k => k.id));
    }
  };

  const handleClearAll = () => {
    setSelectedKeywords([]);
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Filters
          </h2>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            <FunnelIcon className="h-4 w-4" />
            {showFilters ? 'Hide' : 'Show'} Filters
          </button>
        </div>

        {showFilters && (
          <div className="space-y-4">
            {/* Time Range Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Range
              </label>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: '1h', label: '1 Hour' },
                  { value: '6h', label: '6 Hours' },
                  { value: '24h', label: '24 Hours' },
                  { value: '7d', label: '7 Days' },
                  { value: '30d', label: '30 Days' },
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setTimeRange(option.value as any)}
                    className={`px-3 py-1 rounded-md text-sm font-medium ${
                      timeRange === option.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Keyword Filter */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Keywords ({selectedKeywords.length} selected)
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={handleSelectAll}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Select All
                  </button>
                  <button
                    onClick={handleClearAll}
                    className="text-xs text-gray-600 dark:text-gray-400 hover:underline"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {keywords?.keywords?.map((keyword) => (
                  <label
                    key={keyword.id}
                    className="flex items-center gap-2 px-3 py-1 bg-gray-50 dark:bg-gray-700 rounded-md cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                  >
                    <input
                      type="checkbox"
                      checked={selectedKeywords.includes(keyword.id)}
                      onChange={() => handleKeywordToggle(keyword.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {keyword.keyword}
                    </span>
                  </label>
                ))}
              </div>
              {!keywords?.keywords?.length && (
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  No keywords available. Add keywords to see trend analysis.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Trend Dashboard */}
      <TrendMetricsDashboard
        selectedKeywords={selectedKeywords}
        timeRange={timeRange}
        autoRefresh={true}
        refreshInterval={30000}
      />
    </div>
  );
};

export default AnalyticsPage;
