import React, { useState } from 'react';
import { PlayIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { useKeywords } from '../../hooks/useKeywords';
import { Keyword } from '../../types';
import { 
  useStartKeywordCrawl, 
  useStartAllKeywordsCrawl, 
  useStartSubredditCrawl 
} from '../../hooks/useCrawling';

interface CrawlingControlPanelProps {
  onSettingsClick?: () => void;
}

const CrawlingControlPanel: React.FC<CrawlingControlPanelProps> = ({ onSettingsClick }) => {
  const [selectedKeyword, setSelectedKeyword] = useState<number | null>(null);
  const [crawlSettings, setCrawlSettings] = useState({
    limit: 100,
    timeFilter: 'week' as const,
    sort: 'hot' as const,
    includeComments: true,
    commentLimit: 20,
  });
  const [subredditSettings, setSubredditSettings] = useState({
    subredditName: '',
    keywordId: null as number | null,
    limit: 100,
    sort: 'hot' as const,
  });

  const { data: keywordsResponse } = useKeywords();
  const keywords = keywordsResponse?.items || [];
  const activeKeywords = keywords.filter((k: Keyword) => k.is_active);

  const startKeywordCrawl = useStartKeywordCrawl();
  const startAllKeywordsCrawl = useStartAllKeywordsCrawl();
  const startSubredditCrawl = useStartSubredditCrawl();

  const handleStartKeywordCrawl = () => {
    if (!selectedKeyword) return;
    
    startKeywordCrawl.mutate({
      keyword_id: selectedKeyword,
      limit: crawlSettings.limit,
      time_filter: crawlSettings.timeFilter,
      sort: crawlSettings.sort,
      include_comments: crawlSettings.includeComments,
      comment_limit: crawlSettings.commentLimit,
    });
  };

  const handleStartAllKeywordsCrawl = () => {
    startAllKeywordsCrawl.mutate({
      limit_per_keyword: crawlSettings.limit,
      time_filter: crawlSettings.timeFilter,
      sort: crawlSettings.sort,
    });
  };

  const handleStartSubredditCrawl = () => {
    if (!subredditSettings.subredditName || !subredditSettings.keywordId) return;
    
    startSubredditCrawl.mutate({
      subreddit_name: subredditSettings.subredditName,
      keyword_id: subredditSettings.keywordId,
      limit: subredditSettings.limit,
      sort: subredditSettings.sort,
    });
  };

  const isLoading = startKeywordCrawl.isPending || startAllKeywordsCrawl.isPending || startSubredditCrawl.isPending;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Crawling Controls
        </h2>
        {onSettingsClick && (
          <button
            onClick={onSettingsClick}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Cog6ToothIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Single Keyword Crawling */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Single Keyword Crawling
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Keyword
              </label>
              <select
                value={selectedKeyword || ''}
                onChange={(e) => setSelectedKeyword(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select a keyword...</option>
                {activeKeywords.map((keyword: Keyword) => (
                  <option key={keyword.id} value={keyword.id}>
                    {keyword.keyword}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Post Limit
              </label>
              <input
                type="number"
                min="1"
                max="500"
                value={crawlSettings.limit}
                onChange={(e) => setCrawlSettings(prev => ({ ...prev, limit: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Filter
              </label>
              <select
                value={crawlSettings.timeFilter}
                onChange={(e) => setCrawlSettings(prev => ({ ...prev, timeFilter: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="hour">Past Hour</option>
                <option value="day">Past Day</option>
                <option value="week">Past Week</option>
                <option value="month">Past Month</option>
                <option value="year">Past Year</option>
                <option value="all">All Time</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sort By
              </label>
              <select
                value={crawlSettings.sort}
                onChange={(e) => setCrawlSettings(prev => ({ ...prev, sort: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="relevance">Relevance</option>
                <option value="hot">Hot</option>
                <option value="top">Top</option>
                <option value="new">New</option>
                <option value="comments">Comments</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-4 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={crawlSettings.includeComments}
                onChange={(e) => setCrawlSettings(prev => ({ ...prev, includeComments: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Include Comments</span>
            </label>

            {crawlSettings.includeComments && (
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-700 dark:text-gray-300">Comment Limit:</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={crawlSettings.commentLimit}
                  onChange={(e) => setCrawlSettings(prev => ({ ...prev, commentLimit: Number(e.target.value) }))}
                  className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            )}
          </div>

          <button
            onClick={handleStartKeywordCrawl}
            disabled={!selectedKeyword || isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Start Keyword Crawl
          </button>
        </div>

        {/* All Keywords Crawling */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            All Keywords Crawling
          </h3>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Start crawling for all {activeKeywords.length} active keywords simultaneously.
          </p>

          <button
            onClick={handleStartAllKeywordsCrawl}
            disabled={activeKeywords.length === 0 || isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Start All Keywords Crawl
          </button>
        </div>

        {/* Subreddit Crawling */}
        <div>
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Subreddit Crawling
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Subreddit Name
              </label>
              <input
                type="text"
                placeholder="e.g., programming, technology"
                value={subredditSettings.subredditName}
                onChange={(e) => setSubredditSettings(prev => ({ ...prev, subredditName: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Associate with Keyword
              </label>
              <select
                value={subredditSettings.keywordId || ''}
                onChange={(e) => setSubredditSettings(prev => ({ ...prev, keywordId: e.target.value ? Number(e.target.value) : null }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select a keyword...</option>
                {activeKeywords.map((keyword: Keyword) => (
                  <option key={keyword.id} value={keyword.id}>
                    {keyword.keyword}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Post Limit
              </label>
              <input
                type="number"
                min="1"
                max="500"
                value={subredditSettings.limit}
                onChange={(e) => setSubredditSettings(prev => ({ ...prev, limit: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sort By
              </label>
              <select
                value={subredditSettings.sort}
                onChange={(e) => setSubredditSettings(prev => ({ ...prev, sort: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="hot">Hot</option>
                <option value="new">New</option>
                <option value="top">Top</option>
                <option value="rising">Rising</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleStartSubredditCrawl}
            disabled={!subredditSettings.subredditName || !subredditSettings.keywordId || isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Start Subreddit Crawl
          </button>
        </div>
      </div>
    </div>
  );
};

export default CrawlingControlPanel;