import React from 'react';
import { Post } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { ArrowTopRightOnSquareIcon, ChatBubbleLeftIcon, ArrowUpIcon } from '@heroicons/react/24/outline';
import ResponsiveTable from '../ui/ResponsiveTable';

interface PostsTableProps {
  posts: Post[];
  onPostClick: (post: Post) => void;
  loading?: boolean;
}

const PostsTable: React.FC<PostsTableProps> = ({ posts, onPostClick, loading }) => {
  const columns = [
    {
      key: 'title',
      label: 'Title',
      sortable: true,
      render: (title: string, post: Post) => (
        <div className="min-w-0 flex-1">
          <button
            onClick={() => onPostClick(post)}
            className="text-left w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
          >
            <p className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 line-clamp-2">
              {title}
            </p>
          </button>
          {post.content && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-1">
              {post.content.substring(0, 100)}
              {post.content.length > 100 && '...'}
            </p>
          )}
        </div>
      ),
    },
    {
      key: 'author',
      label: 'Author',
      mobileHidden: true,
      render: (author: string, post: Post) => (
        <div className="text-sm text-gray-900 dark:text-gray-100">
          <div>u/{author}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">r/{post.subreddit}</div>
        </div>
      ),
    },
    {
      key: 'score',
      label: 'Score',
      sortable: true,
      className: 'text-center',
      render: (score: number) => (
        <div className="flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
          <ArrowUpIcon className="h-4 w-4 mr-1" />
          <span>{score}</span>
        </div>
      ),
    },
    {
      key: 'num_comments',
      label: 'Comments',
      sortable: true,
      className: 'text-center',
      render: (numComments: number) => (
        <div className="flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
          <ChatBubbleLeftIcon className="h-4 w-4 mr-1" />
          <span>{numComments}</span>
        </div>
      ),
    },
    {
      key: 'post_created_at',
      label: 'Created',
      sortable: true,
      mobileHidden: true,
      render: (createdAt: string) => (
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {formatDistanceToNow(new Date(createdAt), { addSuffix: true })}
        </span>
      ),
    },
    {
      key: 'url',
      label: 'Link',
      className: 'text-center',
      render: (url: string) => (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded"
          onClick={(e) => e.stopPropagation()}
        >
          <ArrowTopRightOnSquareIcon className="h-4 w-4" />
        </a>
      ),
    },
  ];

  return (
    <ResponsiveTable
      columns={columns}
      data={posts}
      loading={loading}
      emptyMessage="No posts found"
      onRowClick={onPostClick}
    />
  );
};

export default PostsTable;