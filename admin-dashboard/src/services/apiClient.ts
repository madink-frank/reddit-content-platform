import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { config, STORAGE_KEYS } from '../config/env';
import { AuthService } from './authService';
import { useUIStore } from '../stores/uiStore';

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

// Extend AxiosRequestConfig to include metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      loadingKey?: string;
      skipErrorNotification?: boolean;
    };
  }
}

class ApiClient {
  private instance: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value: unknown) => void;
    reject: (error: unknown) => void;
  }> = [];

  constructor() {
    this.instance = axios.create({
      baseURL: config.apiBaseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token and handle loading states
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Add request ID for tracking
        config.headers['X-Request-ID'] = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Set loading state for specific operations
        if (config.metadata?.loadingKey) {
          useUIStore.getState().setLoading(config.metadata.loadingKey, true);
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh and loading states
    this.instance.interceptors.response.use(
      (response) => {
        // Clear loading state
        if (response.config.metadata?.loadingKey) {
          useUIStore.getState().setLoading(response.config.metadata.loadingKey, false);
        }
        return response;
      },
      async (error) => {
        // Clear loading state on error
        if (error.config?.metadata?.loadingKey) {
          useUIStore.getState().setLoading(error.config.metadata.loadingKey, false);
        }
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, queue the request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return this.instance(originalRequest);
              })
              .catch((err) => {
                return Promise.reject(err);
              });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            const newTokens = await AuthService.refreshToken(refreshToken);
            
            // Update stored tokens
            localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, newTokens.access_token);
            localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newTokens.refresh_token);
            localStorage.setItem(
              STORAGE_KEYS.TOKEN_EXPIRES_AT,
              (Date.now() + newTokens.expires_in * 1000).toString()
            );

            // Process failed queue
            this.processQueue(null, newTokens.access_token);

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
            return this.instance(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            this.processQueue(refreshError, null);
            this.clearAuthData();
            
            // Redirect to login if not already there
            if (window.location.pathname !== '/login') {
              window.location.href = '/login';
            }
            
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private processQueue(error: unknown, token: string | null) {
    this.failedQueue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token);
      }
    });

    this.failedQueue = [];
  }

  private clearAuthData() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRES_AT);
  }

  private handleError(error: unknown): ApiError {
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response: { data?: { message?: string; code?: string; details?: Record<string, unknown> } } };
      // Server responded with error status
      return {
        message: axiosError.response.data?.message || 'An error occurred',
        code: axiosError.response.data?.code,
        details: axiosError.response.data?.details,
      };
    } else if (error && typeof error === 'object' && 'request' in error) {
      // Request was made but no response received
      return {
        message: 'Network error - please check your connection',
        code: 'NETWORK_ERROR',
      };
    } else {
      // Something else happened
      const errorMessage = error && typeof error === 'object' && 'message' in error 
        ? (error as { message: string }).message 
        : 'An unexpected error occurred';
      return {
        message: errorMessage,
        code: 'UNKNOWN_ERROR',
      };
    }
  }

  // HTTP methods
  async get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.get(url, config);
    return response.data;
  }

  async post<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.post(url, data, config);
    return response.data;
  }

  async put<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.put(url, data, config);
    return response.data;
  }

  async patch<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.patch(url, data, config);
    return response.data;
  }

  async delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.delete(url, config);
    return response.data;
  }

  // HTTP methods with loading key support
  async getWithLoading<T = unknown>(
    url: string,
    loadingKey: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.get<T>(url, {
      ...config,
      metadata: { ...config?.metadata, loadingKey },
    });
  }

  async postWithLoading<T = unknown>(
    url: string,
    data: unknown,
    loadingKey: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.post<T>(url, data, {
      ...config,
      metadata: { ...config?.metadata, loadingKey },
    });
  }

  async putWithLoading<T = unknown>(
    url: string,
    data: unknown,
    loadingKey: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.put<T>(url, data, {
      ...config,
      metadata: { ...config?.metadata, loadingKey },
    });
  }

  async deleteWithLoading<T = unknown>(
    url: string,
    loadingKey: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.delete<T>(url, {
      ...config,
      metadata: { ...config?.metadata, loadingKey },
    });
  }

  // Get the underlying axios instance if needed
  getInstance(): AxiosInstance {
    return this.instance;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;