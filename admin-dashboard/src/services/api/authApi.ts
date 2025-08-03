import { apiClient } from '../apiClient';
import { User, AuthTokens, LoginResponse } from '../../types';

export interface LoginRequest {
  code: string;
  state?: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export const authApi = {
  // OAuth2 login with Reddit
  login: async (request: LoginRequest): Promise<LoginResponse> => {
    return apiClient.post<LoginResponse>('/api/v1/auth/login', request);
  },

  // Refresh access token
  refreshToken: async (request: RefreshTokenRequest): Promise<AuthTokens> => {
    return apiClient.post<AuthTokens>('/api/v1/auth/refresh', request);
  },

  // Get current user profile
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>('/api/v1/auth/me');
  },

  // Logout (invalidate tokens)
  logout: async (): Promise<void> => {
    return apiClient.post<void>('/api/v1/auth/logout');
  },

  // Get Reddit OAuth URL
  getRedditAuthUrl: async (): Promise<{ auth_url: string }> => {
    return apiClient.get<{ auth_url: string }>('/api/v1/auth/reddit-url');
  },
};