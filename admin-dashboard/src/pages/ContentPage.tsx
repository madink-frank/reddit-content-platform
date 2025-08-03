import React, { useState } from 'react';
import { ContentGenerationForm } from '../components/content/ContentGenerationForm';
import { ContentList } from '../components/content/ContentList';
import { ContentEditor } from '../components/content/ContentEditor';
import { ContentGenerationMonitor } from '../components/content/ContentGenerationMonitor';
import { BlogContent } from '../types';
import { 
  PlusIcon, 
  DocumentTextIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const ContentPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'list' | 'generate'>('list');
  const [editingContent, setEditingContent] = useState<BlogContent | null>(null);
  const [viewingContent, setViewingContent] = useState<BlogContent | null>(null);
  const [activeGenerationTasks, setActiveGenerationTasks] = useState<string[]>([]);

  const handleGenerationSuccess = (taskId: string) => {
    setActiveGenerationTasks(prev => [...prev, taskId]);
  };

  const handleGenerationComplete = (taskId: string) => {
    setActiveGenerationTasks(prev => prev.filter(id => id !== taskId));
    // Refresh the content list by switching tabs
    setActiveTab('list');
  };

  const handleGenerationError = (taskId: string) => {
    setActiveGenerationTasks(prev => prev.filter(id => id !== taskId));
  };

  const handleEditContent = (content: BlogContent) => {
    setEditingContent(content);
  };

  const handleViewContent = (content: BlogContent) => {
    setViewingContent(content);
  };

  const handleCloseEditor = () => {
    setEditingContent(null);
  };

  const handleCloseViewer = () => {
    setViewingContent(null);
  };

  const handleSaveContent = (_updatedContent: BlogContent) => {
    setEditingContent(null);
    // The content list will be automatically updated via React Query
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Content Management
        </h1>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('generate')}
            className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium ${
              activeTab === 'generate'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Generate Content
          </button>
          
          <button
            onClick={() => setActiveTab('list')}
            className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium ${
              activeTab === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            Content Library
          </button>
        </div>
      </div>

      {/* Active Generation Tasks */}
      {activeGenerationTasks.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <SparklesIcon className="h-5 w-5 mr-2" />
            Active Generation Tasks
          </h2>
          {activeGenerationTasks.map((taskId) => (
            <ContentGenerationMonitor
              key={taskId}
              taskId={taskId}
              onComplete={() => handleGenerationComplete(taskId)}
              onError={() => handleGenerationError(taskId)}
            />
          ))}
        </div>
      )}

      {/* Main Content */}
      {activeTab === 'generate' ? (
        <ContentGenerationForm onSuccess={handleGenerationSuccess} />
      ) : (
        <ContentList 
          onEdit={handleEditContent}
          onView={handleViewContent}
        />
      )}

      {/* Content Editor Modal */}
      {editingContent && (
        <ContentEditor
          content={editingContent}
          onClose={handleCloseEditor}
          onSave={handleSaveContent}
        />
      )}

      {/* Content Viewer Modal */}
      {viewingContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {viewingContent.title}
              </h2>
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  viewingContent.status === 'published'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : viewingContent.status === 'draft'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                }`}>
                  {viewingContent.status}
                </span>
                <button
                  onClick={handleCloseViewer}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-4 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 8rem)' }}>
              {viewingContent.meta_description && (
                <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                    {viewingContent.meta_description}
                  </p>
                </div>
              )}
              
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: viewingContent.content.replace(/\n/g, '<br>') 
                  }} 
                />
              </div>

              {viewingContent.tags && (
                <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex flex-wrap gap-2">
                    {viewingContent.tags.split(',').map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                      >
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
              <div>
                {viewingContent.word_count} words • Generated {new Date(viewingContent.generated_at).toLocaleDateString()}
              </div>
              <button
                onClick={() => {
                  setViewingContent(null);
                  setEditingContent(viewingContent);
                }}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Edit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentPage;
