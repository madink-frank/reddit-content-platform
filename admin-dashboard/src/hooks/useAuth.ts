import { useCallback, useEffect, useRef } from 'react';
import { useAuth as useAuthContext } from '../contexts/AuthContext';
import { AuthService } from '../services/authService';
import { APP_CONSTANTS } from '../config/env';

export const useAuth = () => {
  const auth = useAuthContext();
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Schedule automatic token refresh
   */
  const scheduleTokenRefresh = useCallback(
    (expiresIn: number) => {
      // Clear existing timeout
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }

      // Schedule refresh 5 minutes before expiry
      const refreshTime = Math.max(
        (expiresIn - APP_CONSTANTS.TOKEN_REFRESH_THRESHOLD) * 1000,
        60000 // Minimum 1 minute
      );

      refreshTimeoutRef.current = setTimeout(async () => {
        if (!auth.tokens?.refresh_token) return;
        
        try {
          const newTokens = await AuthService.refreshToken(auth.tokens.refresh_token);
          auth.updateTokens(newTokens);
          scheduleTokenRefresh(newTokens.expires_in);
        } catch (error) {
          console.error('Token refresh failed:', error);
          auth.logout();
        }
      }, refreshTime);
    },
    [auth.tokens?.refresh_token, auth.updateTokens, auth.logout]
  );

  /**
   * Refresh tokens automatically
   */
  const refreshTokens = useCallback(async () => {
    if (!auth.tokens?.refresh_token) {
      console.warn('No refresh token available');
      return false;
    }

    try {
      const newTokens = await AuthService.refreshToken(auth.tokens.refresh_token);
      auth.updateTokens(newTokens);
      
      // Schedule next refresh
      scheduleTokenRefresh(newTokens.expires_in);
      
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, logout user
      auth.logout();
      return false;
    }
  }, [auth.tokens?.refresh_token, auth.updateTokens, auth.logout, scheduleTokenRefresh]);

  /**
   * Login with OAuth code
   */
  const loginWithCode = useCallback(
    async (code: string, state: string) => {
      try {
        // Validate state parameter
        if (!AuthService.validateOAuthState(state)) {
          throw new Error('Invalid OAuth state parameter');
        }

        const loginResponse = await AuthService.exchangeCodeForTokens({
          code,
          state,
        });

        auth.login(loginResponse.user, loginResponse.tokens);
        
        // Schedule automatic token refresh
        scheduleTokenRefresh(loginResponse.tokens.expires_in);
        
        return true;
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    [auth.login, scheduleTokenRefresh]
  );

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    // Clear refresh timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
      refreshTimeoutRef.current = null;
    }

    // Call logout API if we have a token
    if (auth.tokens?.access_token) {
      try {
        await AuthService.logout(auth.tokens.access_token);
      } catch (error) {
        console.error('Logout API call failed:', error);
        // Continue with local logout even if API call fails
      }
    }

    auth.logout();
  }, [auth.tokens?.access_token, auth.logout]);

  /**
   * Get Reddit OAuth URL
   */
  const getRedditAuthUrl = useCallback(() => {
    return AuthService.getRedditAuthUrl();
  }, []);

  /**
   * Check if current token needs refresh
   */
  const checkTokenExpiry = useCallback(() => {
    if (!auth.tokens?.access_token) return false;
    
    return AuthService.isTokenExpired(auth.tokens.access_token);
  }, [auth.tokens?.access_token]);

  // Set up automatic token refresh on mount and when tokens change
  useEffect(() => {
    if (auth.tokens?.access_token && auth.tokens?.expires_in) {
      // Check if token is already expired or about to expire
      if (checkTokenExpiry()) {
        refreshTokens();
      } else {
        scheduleTokenRefresh(auth.tokens.expires_in);
      }
    }

    // Cleanup timeout on unmount
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [auth.tokens, scheduleTokenRefresh, refreshTokens, checkTokenExpiry]);

  return {
    ...auth,
    loginWithCode,
    logout,
    refreshTokens,
    getRedditAuthUrl,
    checkTokenExpiry,
  };
};