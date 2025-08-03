import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { useUIStore } from '../../stores/uiStore';
import { 
  SunIcon, 
  MoonIcon, 
  ComputerDesktopIcon,
  SwatchIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { Theme } from '../../types';

interface ThemeSettingsProps {
  className?: string;
}

const ThemeSettings: React.FC<ThemeSettingsProps> = ({ className = '' }) => {
  const { theme, setTheme, isDark } = useTheme();
  const { sidebarCollapsed, setSidebarCollapsed } = useUIStore();

  const themeOptions: Array<{
    value: Theme;
    label: string;
    description: string;
    icon: React.ComponentType<{ className?: string }>;
  }> = [
    {
      value: 'light',
      label: 'Light Mode',
      description: 'Use light theme always',
      icon: SunIcon,
    },
    {
      value: 'dark',
      label: 'Dark Mode',
      description: 'Use dark theme always',
      icon: MoonIcon,
    },
    {
      value: 'system',
      label: 'System',
      description: 'Follow system preference',
      icon: ComputerDesktopIcon,
    },
  ];

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
        <SwatchIcon className="w-5 h-5 inline mr-2" />
        Theme & Appearance
      </h3>

      <div className="space-y-6">
        {/* Theme Selection */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Color Theme
          </h4>
          <div className="grid grid-cols-1 gap-3">
            {themeOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = theme === option.value;
              
              return (
                <label
                  key={option.value}
                  className={`relative flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                >
                  <input
                    type="radio"
                    name="theme"
                    value={option.value}
                    checked={isSelected}
                    onChange={() => handleThemeChange(option.value)}
                    className="sr-only"
                  />
                  <div className="flex items-center space-x-3 flex-1">
                    <Icon className={`w-5 h-5 ${isSelected ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'}`} />
                    <div>
                      <div className={`text-sm font-medium ${isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'}`}>
                        {option.label}
                      </div>
                      <div className={`text-xs ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-gray-500 dark:text-gray-400'}`}>
                        {option.description}
                      </div>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="w-4 h-4 bg-blue-600 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  )}
                </label>
              );
            })}
          </div>
        </div>

        {/* Current Theme Preview */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Current Theme Preview
          </h4>
          <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Active Theme:
              </span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                isDark 
                  ? 'bg-gray-800 text-gray-100 border border-gray-600' 
                  : 'bg-gray-100 text-gray-800 border border-gray-300'
              }`}>
                {isDark ? 'Dark' : 'Light'} Mode
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2"></div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-blue-200 dark:bg-blue-800 rounded"></div>
                <div className="h-3 bg-green-200 dark:bg-green-800 rounded w-2/3"></div>
                <div className="h-3 bg-yellow-200 dark:bg-yellow-800 rounded w-3/4"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Layout Settings */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            <EyeIcon className="w-4 h-4 inline mr-2" />
            Layout Settings
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Collapsed Sidebar
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Keep the sidebar collapsed by default
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={sidebarCollapsed}
                  onChange={(e) => setSidebarCollapsed(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Accessibility Settings */}
        <div>
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Accessibility
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Reduce Motion
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Minimize animations and transitions
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  High Contrast
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Increase contrast for better visibility
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemeSettings;