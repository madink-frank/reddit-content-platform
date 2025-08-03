import React, { useState } from 'react';
import { 
  PencilIcon, 
  TrashIcon, 
  MagnifyingGlassIcon,
  PlusIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { Switch } from '@headlessui/react';
import { Keyword } from '../../types';
import { useToggleKeyword, useDeleteKeyword } from '../../hooks/useKeywords';
import LoadingSpinner from '../ui/LoadingSpinner';

interface KeywordListProps {
  keywords: Keyword[];
  isLoading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onEdit: (keyword: Keyword) => void;
  onAdd: () => void;
  activeFilter: 'all' | 'active' | 'inactive';
  onFilterChange: (filter: 'all' | 'active' | 'inactive') => void;
}

export const KeywordList: React.FC<KeywordListProps> = ({
  keywords,
  isLoading,
  searchQuery,
  onSearchChange,
  onEdit,
  onAdd,
  activeFilter,
  onFilterChange,
}) => {
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const toggleKeyword = useToggleKeyword();
  const deleteKeyword = useDeleteKeyword();

  const handleToggle = async (keyword: Keyword) => {
    try {
      await toggleKeyword.mutateAsync(keyword.id);
    } catch (error) {
      console.error('Failed to toggle keyword:', error);
    }
  };

  const handleDelete = async (keyword: Keyword) => {
    if (window.confirm(`Are you sure you want to delete the keyword "${keyword.keyword}"?`)) {
      setDeletingId(keyword.id);
      try {
        await deleteKeyword.mutateAsync(keyword.id);
      } catch (error) {
        console.error('Failed to delete keyword:', error);
      } finally {
        setDeletingId(null);
      }
    }
  };

  const filteredKeywords = keywords.filter(keyword => {
    const matchesSearch = keyword.keyword.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = 
      activeFilter === 'all' || 
      (activeFilter === 'active' && keyword.is_active) ||
      (activeFilter === 'inactive' && !keyword.is_active);
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header with Search and Add Button */}
      <div className="flex flex-col gap-4">
        {/* Top row: Search and Add button */}
        <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search keywords..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              />
            </div>
          </div>

          <button
            onClick={onAdd}
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors whitespace-nowrap"
          >
            <PlusIcon className="h-5 w-5" />
            <span className="hidden sm:inline">Add Keyword</span>
            <span className="sm:hidden">Add</span>
          </button>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-3 overflow-x-auto pb-1">
          <FunnelIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />
          <div className="flex rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden flex-shrink-0">
            {(['all', 'active', 'inactive'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => onFilterChange(filter)}
                className={`px-3 py-1.5 text-sm font-medium capitalize transition-colors whitespace-nowrap ${
                  activeFilter === filter
                    ? 'bg-blue-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Keywords List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredKeywords.length === 0 ? (
          <div className="text-center py-12">
            <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {searchQuery || activeFilter !== 'all' ? 'No keywords found' : 'No keywords yet'}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {searchQuery || activeFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by adding your first keyword.'
              }
            </p>
            {!searchQuery && activeFilter === 'all' && (
              <button
                onClick={onAdd}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
              >
                <PlusIcon className="h-5 w-5" />
                Add Keyword
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredKeywords.map((keyword) => (
              <div
                key={keyword.id}
                className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                {/* Mobile Layout */}
                <div className="sm:hidden space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-medium text-gray-900 dark:text-white truncate">
                        {keyword.keyword}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Created {new Date(keyword.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ml-2 ${
                        keyword.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {keyword.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Status:
                      </span>
                      <Switch
                        checked={keyword.is_active}
                        onChange={() => handleToggle(keyword)}
                        disabled={toggleKeyword.isPending}
                        className={`${
                          keyword.is_active ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-600'
                        } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50`}
                      >
                        <span
                          className={`${
                            keyword.is_active ? 'translate-x-6' : 'translate-x-1'
                          } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                        />
                      </Switch>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onEdit(keyword)}
                        className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-md"
                        title="Edit keyword"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(keyword)}
                        disabled={deletingId === keyword.id}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50 rounded-md"
                        title="Delete keyword"
                      >
                        {deletingId === keyword.id ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <TrashIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Desktop Layout */}
                <div className="hidden sm:flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                        {keyword.keyword}
                      </h3>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          keyword.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {keyword.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Created {new Date(keyword.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    {/* Active/Inactive Toggle */}
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {keyword.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <Switch
                        checked={keyword.is_active}
                        onChange={() => handleToggle(keyword)}
                        disabled={toggleKeyword.isPending}
                        className={`${
                          keyword.is_active ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-600'
                        } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50`}
                      >
                        <span
                          className={`${
                            keyword.is_active ? 'translate-x-6' : 'translate-x-1'
                          } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                        />
                      </Switch>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onEdit(keyword)}
                        className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-md"
                        title="Edit keyword"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(keyword)}
                        disabled={deletingId === keyword.id}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50 rounded-md"
                        title="Delete keyword"
                      >
                        {deletingId === keyword.id ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <TrashIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results Summary */}
      {!isLoading && filteredKeywords.length > 0 && (
        <div className="text-sm text-gray-500 dark:text-gray-400 text-center">
          Showing {filteredKeywords.length} of {keywords.length} keywords
        </div>
      )}
    </div>
  );
};