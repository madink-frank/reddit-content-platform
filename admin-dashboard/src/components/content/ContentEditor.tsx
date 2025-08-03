import React, { useState, useEffect } from 'react';
import { useUpdateContent, useContentTemplates, useRegenerateContent } from '../../hooks/useContent';
import { BlogContent } from '../../types';
import { MarkdownEditor } from './MarkdownEditor';
import LoadingSpinner from '../ui/LoadingSpinner';
import { 
  XMarkIcon, 
  CheckIcon, 
  ArrowPathIcon,
  TagIcon,
  PhotoIcon
} from '@heroicons/react/24/outline';

interface ContentEditorProps {
  content: BlogContent;
  onClose: () => void;
  onSave?: (updatedContent: BlogContent) => void;
}

export const ContentEditor: React.FC<ContentEditorProps> = ({
  content,
  onClose,
  onSave
}) => {
  const [formData, setFormData] = useState({
    title: content.title,
    content: content.content,
    meta_description: content.meta_description || '',
    tags: content.tags ? content.tags.split(',').map(tag => tag.trim()) : [],
    featured_image_url: content.featured_image_url || '',
    status: content.status
  });
  const [newTag, setNewTag] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  const { data: templates } = useContentTemplates();
  const updateMutation = useUpdateContent();
  const regenerateMutation = useRegenerateContent();

  useEffect(() => {
    const hasChanged = 
      formData.title !== content.title ||
      formData.content !== content.content ||
      formData.meta_description !== (content.meta_description || '') ||
      formData.featured_image_url !== (content.featured_image_url || '') ||
      formData.status !== content.status ||
      JSON.stringify(formData.tags) !== JSON.stringify(content.tags ? content.tags.split(',').map(tag => tag.trim()) : []);
    
    setHasChanges(hasChanged);
  }, [formData, content]);

  const handleSave = async () => {
    try {
      const updateData = {
        title: formData.title,
        content: formData.content,
        meta_description: formData.meta_description || undefined,
        tags: formData.tags.length > 0 ? formData.tags : undefined,
        featured_image_url: formData.featured_image_url || undefined,
        status: formData.status as 'draft' | 'published' | 'archived'
      };

      const updatedContent = await updateMutation.mutateAsync({
        id: content.id,
        data: updateData
      });

      onSave?.(updatedContent);
      setHasChanges(false);
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  const handleRegenerate = async (templateType?: string, customPrompt?: string) => {
    if (window.confirm('This will regenerate the content and overwrite current changes. Continue?')) {
      try {
        await regenerateMutation.mutateAsync({
          id: content.id,
          templateType,
          customPrompt
        });
        // The content will be updated via the mutation's onSuccess callback
      } catch (error) {
        console.error('Regeneration failed:', error);
      }
    }
  };

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim()) && formData.tags.length < 10) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Edit Content
          </h2>
          <div className="flex items-center space-x-2">
            {hasChanges && (
              <span className="text-sm text-amber-600 dark:text-amber-400">
                Unsaved changes
              </span>
            )}
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex h-[calc(90vh-8rem)]">
          {/* Left Panel - Form */}
          <div className="w-1/3 p-4 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
            <div className="space-y-4">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              {/* Meta Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Meta Description
                </label>
                <textarea
                  value={formData.meta_description}
                  onChange={(e) => setFormData(prev => ({ ...prev, meta_description: e.target.value }))}
                  rows={3}
                  maxLength={500}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="SEO meta description..."
                />
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {formData.meta_description.length}/500 characters
                </div>
              </div>

              {/* Featured Image */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <PhotoIcon className="h-4 w-4 inline mr-1" />
                  Featured Image URL
                </label>
                <input
                  type="url"
                  value={formData.featured_image_url}
                  onChange={(e) => setFormData(prev => ({ ...prev, featured_image_url: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <TagIcon className="h-4 w-4 inline mr-1" />
                  Tags
                </label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Add tag..."
                    maxLength={50}
                  />
                  <button
                    onClick={handleAddTag}
                    disabled={!newTag.trim() || formData.tags.includes(newTag.trim()) || formData.tags.length >= 10}
                    className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-1">
                  {formData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded"
                    >
                      {tag}
                      <button
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
                      >
                        <XMarkIcon className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {formData.tags.length}/10 tags
                </div>
              </div>

              {/* Regenerate Options */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Regenerate Content
                </h4>
                <div className="space-y-2">
                  <button
                    onClick={() => handleRegenerate()}
                    disabled={regenerateMutation.isPending}
                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <ArrowPathIcon className="h-4 w-4 inline mr-1" />
                    {regenerateMutation.isPending ? 'Regenerating...' : 'Regenerate with Same Template'}
                  </button>
                  
                  {templates && templates.length > 1 && (
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          handleRegenerate(e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      disabled={regenerateMutation.isPending}
                    >
                      <option value="">Regenerate with Different Template...</option>
                      {templates.filter(t => t.name !== content.template_used).map((template) => (
                        <option key={template.name} value={template.name}>
                          {template.description}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Editor */}
          <div className="flex-1 p-4">
            <MarkdownEditor
              value={formData.content}
              onChange={(value) => setFormData(prev => ({ ...prev, content: value }))}
              height="100%"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Last updated: {new Date(content.updated_at).toLocaleString()}
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges || updateMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {updateMutation.isPending ? (
                <>
                  <LoadingSpinner size="sm" className="inline mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckIcon className="h-4 w-4 inline mr-1" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};