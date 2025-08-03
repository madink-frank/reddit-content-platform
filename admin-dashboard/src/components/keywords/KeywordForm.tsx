import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { Keyword, KeywordCreate, KeywordUpdate } from '../../types';
import { useCreateKeyword, useUpdateKeyword } from '../../hooks/useKeywords';
import LoadingSpinner from '../ui/LoadingSpinner';

interface KeywordFormProps {
  keyword?: Keyword;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const KeywordForm: React.FC<KeywordFormProps> = ({
  keyword,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState({
    keyword: '',
    is_active: true,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createKeyword = useCreateKeyword();
  const updateKeyword = useUpdateKeyword();

  const isEditing = !!keyword;
  const isLoading = createKeyword.isPending || updateKeyword.isPending;

  // Reset form when modal opens/closes or keyword changes
  useEffect(() => {
    if (isOpen) {
      if (keyword) {
        setFormData({
          keyword: keyword.keyword,
          is_active: keyword.is_active,
        });
      } else {
        setFormData({
          keyword: '',
          is_active: true,
        });
      }
      setErrors({});
    }
  }, [isOpen, keyword]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.keyword.trim()) {
      newErrors.keyword = 'Keyword is required';
    } else if (formData.keyword.trim().length < 2) {
      newErrors.keyword = 'Keyword must be at least 2 characters long';
    } else if (formData.keyword.trim().length > 100) {
      newErrors.keyword = 'Keyword must be less than 100 characters';
    } else if (!/^[a-zA-Z0-9\s\-_]+$/.test(formData.keyword.trim())) {
      newErrors.keyword = 'Keyword can only contain letters, numbers, spaces, hyphens, and underscores';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const keywordData = formData.keyword.trim();

      if (isEditing && keyword) {
        const updateData: KeywordUpdate = {};
        
        // Only include changed fields
        if (keywordData !== keyword.keyword) {
          updateData.keyword = keywordData;
        }
        if (formData.is_active !== keyword.is_active) {
          updateData.is_active = formData.is_active;
        }

        // Only update if there are changes
        if (Object.keys(updateData).length > 0) {
          await updateKeyword.mutateAsync({ id: keyword.id, data: updateData });
        }
      } else {
        const createData: KeywordCreate = {
          keyword: keywordData,
        };
        await createKeyword.mutateAsync(createData);
      }

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Failed to save keyword:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  // Real-time validation for keyword field
  const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleInputChange(e);
    
    const value = e.target.value.trim();
    if (value && !/^[a-zA-Z0-9\s\-_]*$/.test(value)) {
      setErrors(prev => ({
        ...prev,
        keyword: 'Only letters, numbers, spaces, hyphens, and underscores are allowed',
      }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {isEditing ? 'Edit Keyword' : 'Add New Keyword'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Keyword Input */}
            <div>
              <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Keyword *
              </label>
              <input
                type="text"
                id="keyword"
                name="keyword"
                value={formData.keyword}
                onChange={handleKeywordChange}
                placeholder="Enter keyword (e.g., react, javascript, python)"
                className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.keyword 
                    ? 'border-red-300 dark:border-red-600' 
                    : 'border-gray-300 dark:border-gray-600'
                }`}
                disabled={isLoading}
                autoFocus
              />
              {errors.keyword && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.keyword}
                </p>
              )}
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Keywords are used to search for relevant Reddit posts. Use specific terms for better results.
              </p>
            </div>

            {/* Active Status (only show for editing) */}
            {isEditing && (
              <div>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Active
                  </span>
                </label>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 ml-7">
                  Active keywords will be included in crawling operations.
                </p>
              </div>
            )}

            {/* Form Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 font-medium transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !formData.keyword.trim()}
                className="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading && <LoadingSpinner size="sm" />}
                {isEditing ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};