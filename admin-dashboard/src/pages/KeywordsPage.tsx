import React, { useState } from 'react';
import { useKeywords } from '../hooks/useKeywords';
import { KeywordList } from '../components/keywords/KeywordList';
import { KeywordForm } from '../components/keywords/KeywordForm';
import { Keyword } from '../types';

const KeywordsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingKeyword, setEditingKeyword] = useState<Keyword | undefined>();

  // Build query parameters based on current filters
  const queryParams = {
    page: 1,
    size: 100, // Load all keywords for client-side filtering
    ...(activeFilter !== 'all' && { is_active: activeFilter === 'active' }),
    ...(searchQuery && { search: searchQuery }),
  };

  const { data: keywordsResponse, isLoading, error } = useKeywords(queryParams);
  const keywords = keywordsResponse?.items || [];

  const handleAddKeyword = () => {
    setEditingKeyword(undefined);
    setIsFormOpen(true);
  };

  const handleEditKeyword = (keyword: Keyword) => {
    setEditingKeyword(keyword);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingKeyword(undefined);
  };

  const handleFormSuccess = () => {
    // Form will close automatically and data will be refetched via React Query
  };

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h3 className="text-lg font-medium text-red-800 dark:text-red-200">
            Error Loading Keywords
          </h3>
          <p className="mt-2 text-red-700 dark:text-red-300">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Keywords Management
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage your keywords to control what content gets crawled from Reddit.
        </p>
      </div>

      {/* Keywords List */}
      <KeywordList
        keywords={keywords}
        isLoading={isLoading}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onEdit={handleEditKeyword}
        onAdd={handleAddKeyword}
        activeFilter={activeFilter}
        onFilterChange={setActiveFilter}
      />

      {/* Keyword Form Modal */}
      <KeywordForm
        keyword={editingKeyword}
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        onSuccess={handleFormSuccess}
      />
    </div>
  );
};

export default KeywordsPage;
