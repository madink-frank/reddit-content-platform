// Store type definitions
export interface AppState {
  // Global app settings
  isOnline: boolean;
  lastActivity: number;
  
  // Feature flags
  features: {
    analytics: boolean;
    notifications: boolean;
    realTimeUpdates: boolean;
  };
  
  // Actions
  setOnlineStatus: (isOnline: boolean) => void;
  updateLastActivity: () => void;
  toggleFeature: (feature: keyof AppState['features']) => void;
}

export interface UIState {
  // Layout state
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  
  // Modal and overlay state
  modals: {
    [key: string]: boolean;
  };
  
  // Loading states for different operations
  loadingStates: {
    [key: string]: boolean;
  };
  
  // Actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;
  setLoading: (key: string, loading: boolean) => void;
}

export interface NotificationItem {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  timestamp: number;
  read: boolean;
}

export interface NotificationState {
  notifications: NotificationItem[];
  unreadCount: number;
  
  // Actions
  addNotification: (notification: Omit<NotificationItem, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
}