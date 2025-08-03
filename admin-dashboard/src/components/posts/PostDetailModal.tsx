import React from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { XMarkIcon, ArrowTopRightOnSquareIcon, ArrowUpIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';
import { PostDetail } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import LoadingSpinner from '../ui/LoadingSpinner';

interface PostDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  post: PostDetail | null;
  loading?: boolean;
}

const PostDetailModal: React.FC<PostDetailModalProps> = ({ isOpen, onClose, post, loading }) => {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900 dark:text-white">
                    Post Details
                  </Dialog.Title>
                  <button
                    type="button"
                    className="rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onClick={onClose}
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                {loading ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : post ? (
                  <div className="space-y-6">
                    {/* Post Header */}
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
                      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        {post.title}
                      </h2>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                          <span>by u/{post.author}</span>
                          <span>in r/{post.subreddit}</span>
                          <span>{formatDistanceToNow(new Date(post.post_created_at), { addSuffix: true })}</span>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                            <ArrowUpIcon className="h-4 w-4 mr-1" />
                            <span>{post.score}</span>
                          </div>
                          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                            <ChatBubbleLeftIcon className="h-4 w-4 mr-1" />
                            <span>{post.num_comments}</span>
                          </div>
                          <a
                            href={post.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800"
                          >
                            <ArrowTopRightOnSquareIcon className="h-4 w-4 mr-1" />
                            View on Reddit
                          </a>
                        </div>
                      </div>
                    </div>

                    {/* Post Content */}
                    {post.content && (
                      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Content</h3>
                        <div className="prose dark:prose-invert max-w-none">
                          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                            {post.content}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Comments */}
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Comments ({post.comments.length})
                      </h3>
                      {post.comments.length > 0 ? (
                        <div className="space-y-4 max-h-96 overflow-y-auto">
                          {post.comments.map((comment) => (
                            <div
                              key={comment.id}
                              className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                                  <span className="font-medium">u/{comment.author}</span>
                                  <span>•</span>
                                  <span>
                                    {formatDistanceToNow(new Date(comment.comment_created_at), { addSuffix: true })}
                                  </span>
                                </div>
                                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                                  <ArrowUpIcon className="h-4 w-4 mr-1" />
                                  <span>{comment.score}</span>
                                </div>
                              </div>
                              <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                                {comment.body}
                              </p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 dark:text-gray-400">No comments available</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400">Post not found</p>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default PostDetailModal;