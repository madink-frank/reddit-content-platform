import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, AuthTokens } from '../types';
import { STORAGE_KEYS } from '../config/env';

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  updateTokens: (tokens: AuthTokens) => void;
  tokenExpiresAt: number | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [tokenExpiresAt, setTokenExpiresAt] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load user and tokens from localStorage on app start
    const loadStoredAuth = () => {
      try {
        const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
        const storedAccessToken = localStorage.getItem(
          STORAGE_KEYS.ACCESS_TOKEN
        );
        const storedRefreshToken = localStorage.getItem(
          STORAGE_KEYS.REFRESH_TOKEN
        );

        if (storedUser && storedAccessToken && storedRefreshToken) {
          const parsedUser = JSON.parse(storedUser);
          const storedExpiresAt = localStorage.getItem(STORAGE_KEYS.TOKEN_EXPIRES_AT);
          const expiresAt = storedExpiresAt ? parseInt(storedExpiresAt, 10) : Date.now() + 3600 * 1000;
          
          const parsedTokens: AuthTokens = {
            access_token: storedAccessToken,
            refresh_token: storedRefreshToken,
            token_type: 'bearer',
            expires_in: Math.max(0, Math.floor((expiresAt - Date.now()) / 1000)),
          };

          setUser(parsedUser);
          setTokens(parsedTokens);
          setTokenExpiresAt(expiresAt);
        }
      } catch (error) {
        console.error('Error loading stored auth:', error);
        // Clear invalid stored data
        localStorage.removeItem(STORAGE_KEYS.USER);
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRES_AT);
      } finally {
        setIsLoading(false);
      }
    };

    loadStoredAuth();
  }, []);

  const login = (user: User, tokens: AuthTokens) => {
    const expiresAt = Date.now() + tokens.expires_in * 1000;
    
    setUser(user);
    setTokens(tokens);
    setTokenExpiresAt(expiresAt);

    // Store in localStorage
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
    localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRES_AT, expiresAt.toString());
  };

  const logout = () => {
    setUser(null);
    setTokens(null);
    setTokenExpiresAt(null);

    // Clear localStorage
    localStorage.removeItem(STORAGE_KEYS.USER);
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRES_AT);
  };

  const updateTokens = (newTokens: AuthTokens) => {
    const expiresAt = Date.now() + newTokens.expires_in * 1000;
    
    setTokens(newTokens);
    setTokenExpiresAt(expiresAt);
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, newTokens.access_token);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newTokens.refresh_token);
    localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRES_AT, expiresAt.toString());
  };

  const isAuthenticated = !!(user && tokens);

  const value: AuthContextType = {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateTokens,
    tokenExpiresAt,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
