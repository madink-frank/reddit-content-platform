import axios, { AxiosResponse } from 'axios';
import { config, API_ENDPOINTS } from '../config/env';
import { LoginResponse, AuthTokens, User } from '../types';

// Create axios instance for auth service (no interceptors to avoid circular dependencies)
const authApi = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 10000,
});

export interface AuthCallbackParams {
  code: string;
  state: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export class AuthService {
  /**
   * Exchange OAuth code for tokens
   */
  static async exchangeCodeForTokens(
    params: AuthCallbackParams
  ): Promise<LoginResponse> {
    try {
      const response: AxiosResponse<LoginResponse> = await authApi.post(
        API_ENDPOINTS.auth.login,
        {
          code: params.code,
          state: params.state,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Token exchange failed:', error);
      throw new Error('Failed to authenticate with Reddit');
    }
  }

  /**
   * Refresh access token using refresh token
   */
  static async refreshToken(refreshToken: string): Promise<AuthTokens> {
    try {
      const response: AxiosResponse<AuthTokens> = await authApi.post(
        API_ENDPOINTS.auth.refresh,
        {
          refresh_token: refreshToken,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw new Error('Failed to refresh authentication token');
    }
  }

  /**
   * Get current user info
   */
  static async getCurrentUser(accessToken: string): Promise<User> {
    try {
      const response: AxiosResponse<User> = await authApi.get(
        API_ENDPOINTS.auth.me,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Get current user failed:', error);
      throw new Error('Failed to get user information');
    }
  }

  /**
   * Logout user (invalidate tokens)
   */
  static async logout(accessToken: string): Promise<void> {
    try {
      await authApi.post(
        API_ENDPOINTS.auth.logout,
        {},
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
    } catch (error) {
      console.error('Logout failed:', error);
      // Don't throw error for logout - we'll clear local storage anyway
    }
  }

  /**
   * Check if token is expired or about to expire
   */
  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      // Consider token expired if it expires within 5 minutes
      return payload.exp <= currentTime + 300;
    } catch (error) {
      console.error('Error checking token expiry:', error);
      return true; // Assume expired if we can't parse
    }
  }

  /**
   * Generate Reddit OAuth URL
   */
  static getRedditAuthUrl(): string {
    const state = Math.random().toString(36).substring(2, 15);
    const params = new URLSearchParams({
      client_id: config.redditClientId,
      response_type: 'code',
      state,
      redirect_uri: config.redditRedirectUri,
      duration: 'permanent',
      scope: 'identity read',
    });

    // Store state for validation
    sessionStorage.setItem('oauth_state', state);

    return `https://www.reddit.com/api/v1/authorize?${params.toString()}`;
  }

  /**
   * Validate OAuth state parameter
   */
  static validateOAuthState(state: string): boolean {
    const storedState = sessionStorage.getItem('oauth_state');
    sessionStorage.removeItem('oauth_state'); // Clean up
    return storedState === state;
  }
}