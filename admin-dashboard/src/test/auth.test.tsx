import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../contexts/AuthContext';
import { useAuth } from '../hooks/useAuth';
import LoginPage from '../pages/LoginPage';
import ProtectedRoute from '../components/auth/ProtectedRoute';
import { AuthService } from '../services/authService';

// Mock AuthService
vi.mock('../services/authService', () => ({
  AuthService: {
    exchangeCodeForTokens: vi.fn(),
    refreshToken: vi.fn(),
    logout: vi.fn(),
    getRedditAuthUrl: vi.fn(),
    validateOAuthState: vi.fn(),
    isTokenExpired: vi.fn(),
  },
}));

// Mock environment config
vi.mock('../config/env', () => ({
  config: {
    redditClientId: 'test-client-id',
    redditRedirectUri: 'http://localhost:5173/auth/callback',
  },
  STORAGE_KEYS: {
    ACCESS_TOKEN: 'test_access_token',
    REFRESH_TOKEN: 'test_refresh_token',
    USER: 'test_user',
    TOKEN_EXPIRES_AT: 'test_expires_at',
  },
  APP_CONSTANTS: {
    TOKEN_REFRESH_THRESHOLD: 300000,
  },
}));

// Test component that uses auth
const TestComponent = () => {
  const { user, isAuthenticated, loginWithCode, logout } = useAuth();
  
  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'authenticated' : 'not-authenticated'}
      </div>
      {user && <div data-testid="user-name">{user.name}</div>}
      <button onClick={() => loginWithCode('test-code', 'test-state')}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>{component}</AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Authentication System', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('AuthContext', () => {
    it('should start with unauthenticated state', async () => {
      renderWithProviders(<TestComponent />);
      
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated');
      });
    });

    it('should load stored authentication data on mount', async () => {
      // Set up stored auth data
      const mockUser = { 
        id: 1, 
        name: 'Test User', 
        email: 'test@example.com',
        oauth_provider: 'reddit',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };
      const mockTokens = {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        token_type: 'bearer',
        expires_in: 3600,
      };

      localStorage.setItem('test_user', JSON.stringify(mockUser));
      localStorage.setItem('test_access_token', mockTokens.access_token);
      localStorage.setItem('test_refresh_token', mockTokens.refresh_token);
      localStorage.setItem('test_expires_at', (Date.now() + 3600000).toString());

      renderWithProviders(<TestComponent />);

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
        expect(screen.getByTestId('user-name')).toHaveTextContent('Test User');
      });
    });

    it('should handle login with OAuth code', async () => {
      const mockUser = { 
        id: 1, 
        name: 'Test User', 
        email: 'test@example.com',
        oauth_provider: 'reddit',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };
      const mockTokens = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
        expires_in: 3600,
      };

      vi.mocked(AuthService.validateOAuthState).mockReturnValue(true);
      vi.mocked(AuthService.exchangeCodeForTokens).mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });

      renderWithProviders(<TestComponent />);

      fireEvent.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
        expect(screen.getByTestId('user-name')).toHaveTextContent('Test User');
      });

      // Check that tokens are stored
      expect(localStorage.getItem('test_access_token')).toBe('new-access-token');
      expect(localStorage.getItem('test_refresh_token')).toBe('new-refresh-token');
    });

    it('should handle logout', async () => {
      // Set up authenticated state
      const mockUser = { 
        id: 1, 
        name: 'Test User', 
        email: 'test@example.com',
        oauth_provider: 'reddit',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };
      localStorage.setItem('test_user', JSON.stringify(mockUser));
      localStorage.setItem('test_access_token', 'test-token');
      localStorage.setItem('test_refresh_token', 'test-refresh');

      renderWithProviders(<TestComponent />);

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      });

      fireEvent.click(screen.getByText('Logout'));

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated');
      });

      // Check that tokens are cleared
      expect(localStorage.getItem('test_access_token')).toBeNull();
      expect(localStorage.getItem('test_refresh_token')).toBeNull();
      expect(localStorage.getItem('test_user')).toBeNull();
    });
  });

  describe('LoginPage', () => {
    it('should render login button', () => {
      vi.mocked(AuthService.getRedditAuthUrl).mockReturnValue('https://reddit.com/auth');
      
      renderWithProviders(<LoginPage />);
      
      expect(screen.getByText('Sign in with Reddit')).toBeInTheDocument();
    });

    it('should handle OAuth callback with code', async () => {
      const mockUser = { 
        id: 1, 
        name: 'Test User', 
        email: 'test@example.com',
        oauth_provider: 'reddit',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };
      const mockTokens = {
        access_token: 'callback-token',
        refresh_token: 'callback-refresh',
        token_type: 'bearer',
        expires_in: 3600,
      };

      vi.mocked(AuthService.validateOAuthState).mockReturnValue(true);
      vi.mocked(AuthService.exchangeCodeForTokens).mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });

      // Mock URL search params
      const mockSearchParams = new URLSearchParams('?code=test-code&state=test-state');
      vi.stubGlobal('location', {
        search: mockSearchParams.toString(),
      });

      renderWithProviders(<LoginPage />);

      await waitFor(() => {
        expect(AuthService.exchangeCodeForTokens).toHaveBeenCalledWith({
          code: 'test-code',
          state: 'test-state',
        });
      });
    });

    it('should show error for invalid OAuth state', async () => {
      vi.mocked(AuthService.validateOAuthState).mockReturnValue(false);

      const mockSearchParams = new URLSearchParams('?code=test-code&state=invalid-state');
      vi.stubGlobal('location', {
        search: mockSearchParams.toString(),
      });

      renderWithProviders(<LoginPage />);

      await waitFor(() => {
        expect(screen.getByText(/Invalid OAuth state parameter/)).toBeInTheDocument();
      });
    });
  });

  describe('ProtectedRoute', () => {
    it('should render children when authenticated', async () => {
      // Set up authenticated state
      const mockUser = { 
        id: 1, 
        name: 'Test User', 
        email: 'test@example.com',
        oauth_provider: 'reddit',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };
      localStorage.setItem('test_user', JSON.stringify(mockUser));
      localStorage.setItem('test_access_token', 'test-token');
      localStorage.setItem('test_refresh_token', 'test-refresh');

      renderWithProviders(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      });
    });

    it('should redirect to login when not authenticated', async () => {
      renderWithProviders(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      await waitFor(() => {
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
      });
    });
  });
});