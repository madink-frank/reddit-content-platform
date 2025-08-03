import React, { useState } from 'react';
import { EyeIcon, PencilIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  height?: string;
  readOnly?: boolean;
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  value,
  onChange,
  placeholder = "Start writing your content in Markdown...",
  height = "400px",
  readOnly = false
}) => {
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit');
  const [copied, setCopied] = useState(false);

  // Simple markdown to HTML converter for preview
  const markdownToHtml = (markdown: string): string => {
    let html = markdown;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 mt-4">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4 mt-8">$1</h1>');
    
    // Bold and italic
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
    
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 dark:bg-gray-800 rounded p-3 my-3 overflow-x-auto"><code class="text-sm">$1</code></pre>');
    html = html.replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm">$1</code>');
    
    // Lists
    html = html.replace(/^\* (.*$)/gim, '<li class="ml-4">• $1</li>');
    html = html.replace(/^- (.*$)/gim, '<li class="ml-4">• $1</li>');
    html = html.replace(/^\d+\. (.*$)/gim, '<li class="ml-4 list-decimal">$1</li>');
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 dark:text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Line breaks
    html = html.replace(/\n\n/g, '</p><p class="mb-3">');
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in paragraphs
    html = '<p class="mb-3">' + html + '</p>';
    
    return html;
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getWordCount = (text: string): number => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  const getReadingTime = (text: string): number => {
    const wordCount = getWordCount(text);
    return Math.ceil(wordCount / 200); // Assuming 200 words per minute
  };

  return (
    <div className="border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 px-4 py-2 border-b border-gray-300 dark:border-gray-600">
        <div className="flex space-x-1">
          <button
            onClick={() => setActiveTab('edit')}
            className={`px-3 py-1 text-sm font-medium rounded ${
              activeTab === 'edit'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
            disabled={readOnly}
          >
            <PencilIcon className="h-4 w-4 inline mr-1" />
            Edit
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-3 py-1 text-sm font-medium rounded ${
              activeTab === 'preview'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <EyeIcon className="h-4 w-4 inline mr-1" />
            Preview
          </button>
        </div>

        <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
          <span>{getWordCount(value)} words</span>
          <span>{getReadingTime(value)} min read</span>
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1 hover:text-gray-700 dark:hover:text-gray-300"
            title="Copy to clipboard"
          >
            <DocumentDuplicateIcon className="h-4 w-4" />
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ height }}>
        {activeTab === 'edit' ? (
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            readOnly={readOnly}
            className="w-full h-full p-4 border-none resize-none focus:outline-none focus:ring-0 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
            style={{ minHeight: height }}
          />
        ) : (
          <div 
            className="h-full p-4 overflow-y-auto bg-white dark:bg-gray-800 prose prose-sm dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: markdownToHtml(value) }}
          />
        )}
      </div>

      {/* Footer with markdown help */}
      {activeTab === 'edit' && !readOnly && (
        <div className="bg-gray-50 dark:bg-gray-700 px-4 py-2 border-t border-gray-300 dark:border-gray-600">
          <div className="text-xs text-gray-500 dark:text-gray-400 flex flex-wrap gap-4">
            <span><strong>**bold**</strong></span>
            <span><em>*italic*</em></span>
            <span><code>`code`</code></span>
            <span># Header</span>
            <span>- List item</span>
            <span>[Link](url)</span>
          </div>
        </div>
      )}
    </div>
  );
};