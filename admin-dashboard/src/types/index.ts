// API Response Types
export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Posts API specific response format
export interface PostListResponse {
  posts: Post[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// User and Authentication Types
export interface User {
  id: number;
  name: string;
  email: string;
  oauth_provider: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

// Keyword Types
export interface Keyword {
  id: number;
  user_id: number;
  keyword: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface KeywordCreate {
  keyword: string;
}

export interface KeywordUpdate {
  keyword?: string;
  is_active?: boolean;
}

// Post Types
export interface Post {
  id: number;
  keyword_id: number;
  reddit_id: string;
  title: string;
  content: string | null;
  author: string;
  score: number;
  num_comments: number;
  url: string;
  subreddit: string;
  post_created_at: string;
  created_at: string;
  updated_at: string;
}

export interface PostDetail extends Post {
  comments: Comment[];
}

// Comment Types
export interface Comment {
  id: number;
  reddit_id: string;
  body: string;
  author: string;
  score: number;
  comment_created_at: string;
  created_at: string;
  updated_at: string;
}

// Trend Analysis Types
export interface TrendMetrics {
  id: number;
  post_id: number;
  engagement_score: number;
  tfidf_score: number;
  trend_velocity: number;
  calculated_at: string;
}

export interface TrendData {
  keyword: string;
  metrics: TrendMetrics[];
  summary: {
    total_posts: number;
    avg_engagement: number;
    trend_direction: 'up' | 'down' | 'stable';
  };
}

// Content Generation Types
export interface BlogContent {
  id: number;
  keyword_id: number;
  title: string;
  content: string;
  template_used: string;
  generated_at: string;
  word_count: number;
  status: 'draft' | 'published' | 'archived';
  slug?: string;
  meta_description?: string;
  tags?: string;
  featured_image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ContentTemplate {
  name: string;
  description: string;
  variables: string[];
  example?: string;
}

export interface ContentGenerationRequest {
  keyword_id: number;
  template_type: string;
  include_trends: boolean;
  include_top_posts: boolean;
  max_posts: number;
  custom_prompt?: string;
}

export interface ContentGenerationResponse {
  task_id: string;
  status: string;
  message: string;
  estimated_completion?: string;
}

export interface ContentGenerationStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: BlogContent;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface ContentPreview {
  title: string;
  content_preview: string;
  word_count: number;
  estimated_read_time: number;
  tags: string[];
  template_used: string;
}

// Task and Process Types
export interface ProcessLog {
  id: number;
  user_id: number;
  task_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  task_id: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  result?: unknown;
}

// System Health Types
export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  services: {
    database: boolean;
    redis: boolean;
    reddit_api: boolean;
    celery: boolean;
  };
  timestamp: string;
}

// Chart and Analytics Types
export interface ChartDataPoint {
  x: string | number;
  y: number;
  label?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// Theme Types
export type Theme = 'light' | 'dark' | 'system';

// Environment Configuration
export interface AppConfig {
  apiBaseUrl: string;
  wsUrl: string;
  redditClientId: string;
  redditRedirectUri: string;
  environment: 'development' | 'staging' | 'production';
  features: {
    analytics: boolean;
    notifications: boolean;
  };
  adminUsernames: string[];
}
