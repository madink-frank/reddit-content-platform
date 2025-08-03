import React, { useState, useEffect } from 'react';
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, MinusIcon, WifiIcon } from '@heroicons/react/24/outline';
import TrendChart from './TrendChart';
import KeywordComparisonChart from './KeywordComparisonChart';
import TfIdfChart from './TfIdfChart';
import MetricCard from './MetricCard';
import { TrendData } from '../../types';
import { useTrends, useAnalyzeTrends } from '../../hooks/useTrends';
import { useKeywords } from '../../hooks/useKeywords';
import { useRealtimeTrends } from '../../hooks/useRealtimeTrends';

interface TrendMetricsDashboardProps {
  selectedKeywords?: number[];
  timeRange?: '1h' | '6h' | '24h' | '7d' | '30d';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const TrendMetricsDashboard: React.FC<TrendMetricsDashboardProps> = ({
  selectedKeywords = [],
  timeRange = '24h',
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'comparison' | 'tfidf'>('overview');
  const [selectedMetric, setSelectedMetric] = useState<'engagement_score' | 'tfidf_score' | 'trend_velocity'>('engagement_score');

  const { data: keywordsData } = useKeywords();
  const { data: trendsData, isLoading, refetch } = useTrends({ time_range: timeRange });
  const analyzeTrendsMutation = useAnalyzeTrends();
  const { isConnected, subscribeToAllTrends, unsubscribeFromAllTrends } = useRealtimeTrends(autoRefresh);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refetch();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refetch]);

  // Subscribe to real-time trend updates
  useEffect(() => {
    if (autoRefresh) {
      subscribeToAllTrends();
      return () => unsubscribeFromAllTrends();
    }
  }, [autoRefresh, subscribeToAllTrends, unsubscribeFromAllTrends]);

  const handleAnalyzeTrends = () => {
    analyzeTrendsMutation.mutate(selectedKeywords.length > 0 ? selectedKeywords : undefined);
  };

  const getFilteredTrendsData = (): TrendData[] => {
    if (!trendsData?.trends) return [];
    
    if (selectedKeywords.length === 0) {
      return trendsData.trends;
    }
    
    return trendsData.trends.filter(trend => {
      const keyword = keywordsData?.keywords?.find(k => k.keyword === trend.keyword);
      return keyword && selectedKeywords.includes(keyword.id);
    });
  };

  const getTfIdfData = () => {
    const filteredTrends = getFilteredTrendsData();
    return filteredTrends.map(trend => ({
      keyword: trend.keyword,
      tfidf_score: trend.metrics.length > 0 
        ? trend.metrics[trend.metrics.length - 1].tfidf_score 
        : 0,
      post_count: trend.summary.total_posts,
    }));
  };

  const getSummaryStats = () => {
    if (!trendsData?.summary) {
      return {
        total_keywords: 0,
        trending_up: 0,
        trending_down: 0,
        stable: 0,
      };
    }
    return trendsData.summary;
  };

  const summaryStats = getSummaryStats();
  const filteredTrends = getFilteredTrendsData();

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Trend Analytics Dashboard
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Real-time trend analysis and keyword performance metrics
          </p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={handleAnalyzeTrends}
            disabled={analyzeTrendsMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <ChartBarIcon className="h-4 w-4" />
            {analyzeTrendsMutation.isPending ? 'Analyzing...' : 'Analyze Trends'}
          </button>
          
          <button
            onClick={() => refetch()}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>

          {/* Real-time connection indicator */}
          <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <WifiIcon className={`h-4 w-4 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Keywords"
          value={summaryStats.total_keywords}
          icon={<ChartBarIcon className="h-5 w-5" />}
        />
        
        <MetricCard
          title="Trending Up"
          value={summaryStats.trending_up}
          trend="up"
          icon={<ArrowTrendingUpIcon className="h-5 w-5" />}
        />
        
        <MetricCard
          title="Trending Down"
          value={summaryStats.trending_down}
          trend="down"
          icon={<ArrowTrendingDownIcon className="h-5 w-5" />}
        />
        
        <MetricCard
          title="Stable"
          value={summaryStats.stable}
          trend="stable"
          icon={<MinusIcon className="h-5 w-5" />}
        />
      </div>

      {/* Additional Metrics */}
      {trendsData?.top_keywords && trendsData.top_keywords.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Top Engagement Score"
            value={trendsData.top_keywords[0]?.engagement_score || 0}
            format="decimal"
            className="border-l-4 border-blue-500"
          />
          
          <MetricCard
            title="Top TF-IDF Score"
            value={Math.max(...trendsData.top_keywords.map(k => k.engagement_score)) || 0}
            format="decimal"
            className="border-l-4 border-green-500"
          />
          
          <MetricCard
            title="Top Trend Velocity"
            value={Math.max(...trendsData.top_keywords.map(k => k.trend_velocity)) || 0}
            format="decimal"
            className="border-l-4 border-purple-500"
          />
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'comparison', label: 'Keyword Comparison' },
            { id: 'tfidf', label: 'TF-IDF Analysis' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Chart Content */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {filteredTrends.length > 0 ? (
              filteredTrends.map((trend) => (
                <div key={trend.keyword} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {trend.keyword}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span>Posts: {trend.summary.total_posts}</span>
                      <span>Avg Engagement: {trend.summary.avg_engagement.toFixed(2)}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        trend.summary.trend_direction === 'up' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : trend.summary.trend_direction === 'down'
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                        {trend.summary.trend_direction}
                      </span>
                    </div>
                  </div>
                  <TrendChart
                    data={trend.metrics}
                    title={`${trend.keyword} - Trend Analysis`}
                    height={300}
                  />
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">No trend data available</p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                  Click "Analyze Trends" to generate trend data
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Metric:
              </label>
              <select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value as any)}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="engagement_score">Engagement Score</option>
                <option value="tfidf_score">TF-IDF Score</option>
                <option value="trend_velocity">Trend Velocity</option>
              </select>
            </div>
            <KeywordComparisonChart
              trendsData={filteredTrends}
              metric={selectedMetric}
              height={500}
            />
          </div>
        )}

        {activeTab === 'tfidf' && (
          <TfIdfChart
            data={getTfIdfData()}
            height={500}
            maxItems={15}
          />
        )}
      </div>
    </div>
  );
};

export default TrendMetricsDashboard;