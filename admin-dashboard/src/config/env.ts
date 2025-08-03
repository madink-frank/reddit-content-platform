import { AppConfig } from '../types';

// Environment variable validation and parsing
const getEnvVar = (key: string, defaultValue?: string): string => {
  const value = import.meta.env[key] || defaultValue;
  if (!value) {
    throw new Error(`Environment variable ${key} is required`);
  }
  return value;
};

const getBooleanEnvVar = (key: string, defaultValue = false): boolean => {
  const value = import.meta.env[key];
  if (value === undefined) return defaultValue;
  return value === 'true' || value === '1';
};

const getArrayEnvVar = (key: string, defaultValue: string[] = []): string[] => {
  const value = import.meta.env[key];
  if (!value) return defaultValue;
  return value
    .split(',')
    .map((item: string) => item.trim())
    .filter(Boolean);
};

// Application configuration
export const config: AppConfig = {
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000/api/v1'),
  wsUrl: getEnvVar('VITE_WS_URL', 'ws://localhost:8000/ws'),
  redditClientId: getEnvVar('VITE_REDDIT_CLIENT_ID'),
  redditRedirectUri: getEnvVar(
    'VITE_REDDIT_REDIRECT_URI',
    'http://localhost:5173/auth/callback'
  ),
  environment: getEnvVar('VITE_NODE_ENV', 'development') as
    | 'development'
    | 'staging'
    | 'production',
  features: {
    analytics: getBooleanEnvVar('VITE_ENABLE_ANALYTICS', true),
    notifications: getBooleanEnvVar('VITE_ENABLE_NOTIFICATIONS', true),
  },
  adminUsernames: getArrayEnvVar('VITE_ADMIN_USERNAMES'),
};

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  auth: {
    login: '/auth/login',
    refresh: '/auth/refresh',
    logout: '/auth/logout',
    me: '/auth/me',
  },
  // Keywords
  keywords: '/keywords',
  // Posts
  posts: '/posts',
  // Crawling
  crawling: {
    start: '/crawling/start',
    status: '/crawling/status',
    history: '/crawling/history',
  },
  // Trends
  trends: '/trends',
  // Content
  content: '/content',
  // Tasks
  tasks: '/tasks',
  // Health
  health: '/health',
} as const;

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'reddit_platform_access_token',
  REFRESH_TOKEN: 'reddit_platform_refresh_token',
  USER: 'reddit_platform_user',
  THEME: 'reddit_platform_theme',
  TOKEN_EXPIRES_AT: 'reddit_platform_token_expires_at',
} as const;

// Application constants
export const APP_CONSTANTS = {
  APP_NAME: 'Reddit Content Platform',
  APP_VERSION: '1.0.0',
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutes before expiry
  NOTIFICATION_DURATION: 5000, // 5 seconds
  POLLING_INTERVAL: 30000, // 30 seconds
} as const;
