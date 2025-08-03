import React, { useState } from 'react';
import { useKeywords } from '../../hooks/useKeywords';
import { useContentTemplates, useGenerateContent, usePreviewContent } from '../../hooks/useContent';
import { ContentGenerationRequest, ContentPreview } from '../../types';
import LoadingSpinner from '../ui/LoadingSpinner';

interface ContentGenerationFormProps {
  onSuccess?: (taskId: string) => void;
  selectedKeywordId?: number;
}

export const ContentGenerationForm: React.FC<ContentGenerationFormProps> = ({
  onSuccess,
  selectedKeywordId
}) => {
  const [formData, setFormData] = useState<ContentGenerationRequest>({
    keyword_id: selectedKeywordId || 0,
    template_type: 'default',
    include_trends: true,
    include_top_posts: true,
    max_posts: 10,
    custom_prompt: ''
  });
  const [showPreview, setShowPreview] = useState(false);
  const [preview, setPreview] = useState<ContentPreview | null>(null);

  const { data: keywords, isLoading: keywordsLoading } = useKeywords();
  const { data: templates, isLoading: templatesLoading } = useContentTemplates();
  const generateMutation = useGenerateContent();
  const previewMutation = usePreviewContent();

  const handleInputChange = (field: keyof ContentGenerationRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setPreview(null); // Clear preview when form changes
  };

  const handlePreview = async () => {
    if (!formData.keyword_id) return;
    
    try {
      const previewData = await previewMutation.mutateAsync(formData);
      setPreview(previewData);
      setShowPreview(true);
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  const handleGenerate = async () => {
    if (!formData.keyword_id) return;
    
    try {
      const result = await generateMutation.mutateAsync(formData);
      onSuccess?.(result.task_id);
      
      // Reset form
      setFormData(prev => ({
        ...prev,
        custom_prompt: ''
      }));
      setPreview(null);
      setShowPreview(false);
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  if (keywordsLoading || templatesLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Generate New Content
      </h3>

      <div className="space-y-4">
        {/* Keyword Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Keyword
          </label>
          <select
            value={formData.keyword_id}
            onChange={(e) => handleInputChange('keyword_id', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value={0}>Select a keyword...</option>
            {keywords?.items.map((keyword) => (
              <option key={keyword.id} value={keyword.id}>
                {keyword.keyword}
              </option>
            ))}
          </select>
        </div>

        {/* Template Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Template
          </label>
          <select
            value={formData.template_type}
            onChange={(e) => handleInputChange('template_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          >
            {templates?.map((template) => (
              <option key={template.name} value={template.name}>
                {template.description}
              </option>
            ))}
          </select>
        </div>

        {/* Generation Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="include_trends"
              checked={formData.include_trends}
              onChange={(e) => handleInputChange('include_trends', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="include_trends" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Include trend analysis
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="include_top_posts"
              checked={formData.include_top_posts}
              onChange={(e) => handleInputChange('include_top_posts', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="include_top_posts" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Include top posts
            </label>
          </div>
        </div>

        {/* Max Posts */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Maximum Posts to Include: {formData.max_posts}
          </label>
          <input
            type="range"
            min="1"
            max="50"
            value={formData.max_posts}
            onChange={(e) => handleInputChange('max_posts', parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>1</span>
            <span>50</span>
          </div>
        </div>

        {/* Custom Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Custom Prompt (Optional)
          </label>
          <textarea
            value={formData.custom_prompt}
            onChange={(e) => handleInputChange('custom_prompt', e.target.value)}
            placeholder="Add any specific instructions or focus areas for content generation..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Preview Section */}
        {preview && showPreview && (
          <div className="border-t pt-4">
            <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">Content Preview</h4>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3">
              <div>
                <h5 className="font-semibold text-gray-900 dark:text-white">{preview.title}</h5>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <div className="flex space-x-4 mb-2">
                  <span>Words: {preview.word_count}</span>
                  <span>Read time: {preview.estimated_read_time} min</span>
                  <span>Template: {preview.template_used}</span>
                </div>
                {preview.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {preview.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {preview.content_preview}
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4">
          <button
            onClick={handlePreview}
            disabled={!formData.keyword_id || previewMutation.isPending}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {previewMutation.isPending ? 'Generating Preview...' : 'Preview'}
          </button>
          
          <button
            onClick={handleGenerate}
            disabled={!formData.keyword_id || generateMutation.isPending}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generateMutation.isPending ? 'Generating...' : 'Generate Content'}
          </button>
        </div>
      </div>
    </div>
  );
};