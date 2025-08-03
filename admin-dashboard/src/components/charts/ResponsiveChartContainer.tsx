import React, { useState, useEffect } from 'react';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

interface ResponsiveChartContainerProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  showToggleOptions?: boolean;
  toggleOptions?: {
    label: string;
    key: string;
    enabled: boolean;
    onChange: (key: string, enabled: boolean) => void;
  }[];
  height?: {
    mobile: number;
    tablet: number;
    desktop: number;
  };
}

const ResponsiveChartContainer: React.FC<ResponsiveChartContainerProps> = ({
  title,
  children,
  className = '',
  showToggleOptions = false,
  toggleOptions = [],
  height = { mobile: 300, tablet: 400, desktop: 500 },
}) => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 640);
      setIsTablet(window.innerWidth >= 640 && window.innerWidth < 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const getHeight = () => {
    if (isMobile) return height.mobile;
    if (isTablet) return height.tablet;
    return height.desktop;
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      {(title || showToggleOptions) && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            {title && (
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {title}
              </h3>
            )}
            
            {showToggleOptions && toggleOptions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {toggleOptions.map((option) => (
                  <button
                    key={option.key}
                    onClick={() => option.onChange(option.key, !option.enabled)}
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      option.enabled
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                    }`}
                  >
                    {option.enabled ? (
                      <EyeIcon className="h-3 w-3" />
                    ) : (
                      <EyeSlashIcon className="h-3 w-3" />
                    )}
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chart content */}
      <div className="p-4">
        <div 
          className="w-full"
          style={{ height: getHeight() }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};

export default ResponsiveChartContainer;