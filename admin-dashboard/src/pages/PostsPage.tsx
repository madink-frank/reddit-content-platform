import React, { useState, useCallback } from 'react';
import { usePosts, usePost } from '../hooks/usePosts';
import { PostListParams } from '../services/api/postsApi';
import { Post } from '../types';
import PostsTable from '../components/posts/PostsTable';
import PostsFilter from '../components/posts/PostsFilter';
import PostDetailModal from '../components/posts/PostDetailModal';
import Pagination from '../components/ui/Pagination';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const PostsPage: React.FC = () => {
  const [filters, setFilters] = useState<PostListParams>({
    page: 1,
    per_page: 10,
    sort_by: 'created_at',
    sort_order: 'desc',
  });
  
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: postsResponse, isLoading, error } = usePosts(filters);
  const { data: selectedPost, isLoading: isPostLoading } = usePost(selectedPostId || 0);

  const handleFiltersChange = useCallback((newFilters: PostListParams) => {
    setFilters({ ...newFilters, page: 1 }); // Reset to first page when filters change
  }, []);

  const handleFiltersReset = useCallback(() => {
    setFilters({
      page: 1,
      per_page: 10,
      sort_by: 'created_at',
      sort_order: 'desc',
    });
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setFilters(prev => ({ ...prev, page }));
  }, []);

  const handlePostClick = useCallback((post: Post) => {
    setSelectedPostId(post.id);
    setIsModalOpen(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setIsModalOpen(false);
    setSelectedPostId(null);
  }, []);

  const handlePerPageChange = useCallback((perPage: number) => {
    setFilters(prev => ({ ...prev, per_page: perPage, page: 1 }));
  }, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Error Loading Posts
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Posts
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            View and manage collected Reddit posts
          </p>
        </div>
        
        {postsResponse && (
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {postsResponse.total} total posts
            </div>
            <select
              value={filters.per_page}
              onChange={(e) => handlePerPageChange(parseInt(e.target.value))}
              className="rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
            >
              <option value={10}>10 per page</option>
              <option value={25}>25 per page</option>
              <option value={50}>50 per page</option>
              <option value={100}>100 per page</option>
            </select>
          </div>
        )}
      </div>

      {/* Filters */}
      <PostsFilter
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onReset={handleFiltersReset}
      />

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      )}

      {/* Posts Table */}
      {!isLoading && postsResponse && (
        <>
          <PostsTable
            posts={postsResponse.posts}
            onPostClick={handlePostClick}
            loading={isLoading}
          />

          {/* Pagination */}
          {postsResponse.total_pages > 1 && (
            <Pagination
              currentPage={postsResponse.page}
              totalPages={postsResponse.total_pages}
              onPageChange={handlePageChange}
              showInfo={true}
              totalItems={postsResponse.total}
              itemsPerPage={postsResponse.per_page}
            />
          )}
        </>
      )}

      {/* Empty State */}
      {!isLoading && postsResponse && postsResponse.posts.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No posts found
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Try adjusting your filters or start crawling some keywords to collect posts.
          </p>
        </div>
      )}

      {/* Post Detail Modal */}
      <PostDetailModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        post={selectedPost || null}
        loading={isPostLoading}
      />
    </div>
  );
};

export default PostsPage;
