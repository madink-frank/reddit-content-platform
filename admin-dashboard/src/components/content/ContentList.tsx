import React, { useState } from 'react';
import { useContent, useDeleteContent } from '../../hooks/useContent';
import { useKeywords } from '../../hooks/useKeywords';
import { BlogContent } from '../../types';
import LoadingSpinner from '../ui/LoadingSpinner';
import Pagination from '../ui/Pagination';
import { 
  EyeIcon, 
  PencilIcon, 
  TrashIcon, 
  ClockIcon,
  DocumentTextIcon,
  TagIcon
} from '@heroicons/react/24/outline';

interface ContentListProps {
  onEdit?: (content: BlogContent) => void;
  onView?: (content: BlogContent) => void;
}

export const ContentList: React.FC<ContentListProps> = ({ onEdit, onView }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedKeyword, setSelectedKeyword] = useState<number | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<'draft' | 'published' | 'archived' | undefined>();

  const { data: contentData, isLoading, error } = useContent({
    page: currentPage,
    size: 10,
    keyword_id: selectedKeyword,
    status: selectedStatus
  });

  const { data: keywordsData } = useKeywords();
  const deleteMutation = useDeleteContent();

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this content? This action cannot be undone.')) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'archived':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const parseTags = (tagsString?: string): string[] => {
    if (!tagsString) return [];
    return tagsString.split(',').map(tag => tag.trim()).filter(Boolean);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-200">
          Failed to load content. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      {/* Filters */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Filter by Keyword
            </label>
            <select
              value={selectedKeyword || ''}
              onChange={(e) => setSelectedKeyword(e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All keywords</option>
              {keywordsData?.items.map((keyword) => (
                <option key={keyword.id} value={keyword.id}>
                  {keyword.keyword}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Filter by Status
            </label>
            <select
              value={selectedStatus || ''}
              onChange={(e) => setSelectedStatus(e.target.value as any || undefined)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All statuses</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content List */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {contentData?.items.length === 0 ? (
          <div className="p-8 text-center">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No content found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Get started by generating your first piece of content.
            </p>
          </div>
        ) : (
          contentData?.items.map((content) => (
            <div key={content.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                      {content.title}
                    </h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(content.status)}`}>
                      {content.status}
                    </span>
                  </div>

                  <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {formatDate(content.generated_at)}
                    </div>
                    <div className="flex items-center">
                      <DocumentTextIcon className="h-4 w-4 mr-1" />
                      {content.word_count} words
                    </div>
                    <div>
                      Template: {content.template_used}
                    </div>
                  </div>

                  {content.meta_description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                      {content.meta_description}
                    </p>
                  )}

                  {content.tags && (
                    <div className="flex items-center space-x-1 mb-2">
                      <TagIcon className="h-4 w-4 text-gray-400" />
                      <div className="flex flex-wrap gap-1">
                        {parseTags(content.tags).slice(0, 3).map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {parseTags(content.tags).length > 3 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            +{parseTags(content.tags).length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => onView?.(content)}
                    className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                    title="View content"
                  >
                    <EyeIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => onEdit?.(content)}
                    className="p-2 text-gray-400 hover:text-green-600 dark:hover:text-green-400"
                    title="Edit content"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(content.id)}
                    disabled={deleteMutation.isPending}
                    className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 disabled:opacity-50"
                    title="Delete content"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {contentData && contentData.pages > 1 && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
          <Pagination
            currentPage={currentPage}
            totalPages={contentData.pages}
            onPageChange={setCurrentPage}
          />
        </div>
      )}
    </div>
  );
};