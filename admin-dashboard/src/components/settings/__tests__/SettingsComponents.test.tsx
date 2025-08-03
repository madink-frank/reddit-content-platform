import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import ProfileSettings from '../ProfileSettings';
import ThemeSettings from '../ThemeSettings';
import NotificationSettings from '../NotificationSettings';
import SystemSettings from '../SystemSettings';
import AccountConnectionStatus from '../AccountConnectionStatus';

// Mock the stores
vi.mock('../../../stores/notificationStore', () => ({
  useNotificationStore: () => ({
    addNotification: vi.fn(),
  }),
}));

vi.mock('../../../stores/appStore', () => ({
  useAppStore: () => ({
    features: {
      analytics: true,
      notifications: true,
      realTimeUpdates: true,
    },
    toggleFeature: vi.fn(),
  }),
}));

vi.mock('../../../stores/uiStore', () => ({
  useUIStore: () => ({
    sidebarCollapsed: false,
    setSidebarCollapsed: vi.fn(),
  }),
}));

// Mock the auth context
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 1,
      name: 'Test User',
      email: 'test@example.com',
      oauth_provider: 'reddit',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    tokens: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
    },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    updateTokens: vi.fn(),
    tokenExpiresAt: Date.now() + 3600000,
  }),
}));

// Mock the theme context
vi.mock('../../../contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'system',
    setTheme: vi.fn(),
    isDark: false,
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
}));

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider>
    {children}
  </ThemeProvider>
);

describe('Settings Components', () => {
  describe('ProfileSettings', () => {
    it('renders user profile information', () => {
      render(
        <TestWrapper>
          <ProfileSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Profile Information')).toBeInTheDocument();
      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      expect(screen.getByText('REDDIT')).toBeInTheDocument();
    });

    it('shows edit profile button', () => {
      render(
        <TestWrapper>
          <ProfileSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });
  });

  describe('ThemeSettings', () => {
    it('renders theme options', () => {
      render(
        <TestWrapper>
          <ThemeSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Theme & Appearance')).toBeInTheDocument();
      expect(screen.getByText('Light Mode')).toBeInTheDocument();
      expect(screen.getByText('Dark Mode')).toBeInTheDocument();
      expect(screen.getByText('System')).toBeInTheDocument();
    });

    it('shows layout settings', () => {
      render(
        <TestWrapper>
          <ThemeSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Layout Settings')).toBeInTheDocument();
      expect(screen.getByText('Collapsed Sidebar')).toBeInTheDocument();
    });
  });

  describe('NotificationSettings', () => {
    it('renders notification preferences', () => {
      render(
        <TestWrapper>
          <NotificationSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Notification Settings')).toBeInTheDocument();
      expect(screen.getByText('Email Notifications')).toBeInTheDocument();
      expect(screen.getByText('Browser Notifications')).toBeInTheDocument();
    });

    it('shows notification types', () => {
      render(
        <TestWrapper>
          <NotificationSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Success Notifications')).toBeInTheDocument();
      expect(screen.getByText('Error Notifications')).toBeInTheDocument();
      expect(screen.getByText('Warning Notifications')).toBeInTheDocument();
      expect(screen.getByText('Info Notifications')).toBeInTheDocument();
    });
  });

  describe('SystemSettings', () => {
    it('renders system configuration options', () => {
      render(
        <TestWrapper>
          <SystemSettings />
        </TestWrapper>
      );

      expect(screen.getByText('System Settings')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Features')).toBeInTheDocument();
    });

    it('shows cache management', () => {
      render(
        <TestWrapper>
          <SystemSettings />
        </TestWrapper>
      );

      expect(screen.getByText('Cache Management')).toBeInTheDocument();
      expect(screen.getByText('Clear Application Cache')).toBeInTheDocument();
    });
  });

  describe('AccountConnectionStatus', () => {
    it('renders connection status information', () => {
      render(
        <TestWrapper>
          <AccountConnectionStatus />
        </TestWrapper>
      );

      expect(screen.getByText('Account & Service Connections')).toBeInTheDocument();
      expect(screen.getByText('Reddit')).toBeInTheDocument();
      expect(screen.getByText('Database')).toBeInTheDocument();
      expect(screen.getByText('Redis Cache')).toBeInTheDocument();
    });

    it('shows refresh all button', () => {
      render(
        <TestWrapper>
          <AccountConnectionStatus />
        </TestWrapper>
      );

      expect(screen.getByText('Refresh All')).toBeInTheDocument();
    });
  });
});