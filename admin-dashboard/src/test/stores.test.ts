import { describe, it, expect, beforeEach } from 'vitest';
import { useAppStore, useUIStore, useNotificationStore } from '../stores';

describe('Zustand Stores', () => {
  beforeEach(() => {
    // Reset stores before each test
    useAppStore.setState({
      isOnline: true,
      lastActivity: Date.now(),
      features: {
        analytics: true,
        notifications: true,
        realTimeUpdates: true,
      },
    });

    useUIStore.setState({
      sidebarCollapsed: false,
      theme: 'system',
      modals: {},
      loadingStates: {},
    });

    useNotificationStore.setState({
      notifications: [],
      unreadCount: 0,
    });
  });

  describe('AppStore', () => {
    it('should initialize with default values', () => {
      const state = useAppStore.getState();
      expect(state.isOnline).toBe(true);
      expect(state.features.analytics).toBe(true);
      expect(state.features.notifications).toBe(true);
      expect(state.features.realTimeUpdates).toBe(true);
    });

    it('should toggle features', () => {
      const { toggleFeature } = useAppStore.getState();
      
      toggleFeature('analytics');
      expect(useAppStore.getState().features.analytics).toBe(false);
      
      toggleFeature('analytics');
      expect(useAppStore.getState().features.analytics).toBe(true);
    });

    it('should update online status', () => {
      const { setOnlineStatus } = useAppStore.getState();
      
      setOnlineStatus(false);
      expect(useAppStore.getState().isOnline).toBe(false);
      
      setOnlineStatus(true);
      expect(useAppStore.getState().isOnline).toBe(true);
    });
  });

  describe('UIStore', () => {
    it('should initialize with default values', () => {
      const state = useUIStore.getState();
      expect(state.sidebarCollapsed).toBe(false);
      expect(state.theme).toBe('system');
      expect(state.modals).toEqual({});
      expect(state.loadingStates).toEqual({});
    });

    it('should toggle sidebar', () => {
      const { toggleSidebar } = useUIStore.getState();
      
      toggleSidebar();
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);
      
      toggleSidebar();
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });

    it('should manage modal states', () => {
      const { openModal, closeModal } = useUIStore.getState();
      
      openModal('test-modal');
      expect(useUIStore.getState().modals['test-modal']).toBe(true);
      
      closeModal('test-modal');
      expect(useUIStore.getState().modals['test-modal']).toBe(false);
    });

    it('should manage loading states', () => {
      const { setLoading } = useUIStore.getState();
      
      setLoading('test-operation', true);
      expect(useUIStore.getState().loadingStates['test-operation']).toBe(true);
      
      setLoading('test-operation', false);
      expect(useUIStore.getState().loadingStates['test-operation']).toBe(false);
    });
  });

  describe('NotificationStore', () => {
    it('should initialize with empty notifications', () => {
      const state = useNotificationStore.getState();
      expect(state.notifications).toEqual([]);
      expect(state.unreadCount).toBe(0);
    });

    it('should add notifications', () => {
      const { addNotification } = useNotificationStore.getState();
      
      addNotification({
        type: 'success',
        title: 'Test Notification',
        message: 'This is a test',
        duration: 0, // Don't auto-remove for testing
      });
      
      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
      expect(state.unreadCount).toBe(1);
      expect(state.notifications[0].title).toBe('Test Notification');
      expect(state.notifications[0].read).toBe(false);
    });

    it('should mark notifications as read', () => {
      const { addNotification, markAsRead } = useNotificationStore.getState();
      
      addNotification({
        type: 'info',
        title: 'Test',
        duration: 0,
      });
      
      const notificationId = useNotificationStore.getState().notifications[0].id;
      markAsRead(notificationId);
      
      const state = useNotificationStore.getState();
      expect(state.notifications[0].read).toBe(true);
      expect(state.unreadCount).toBe(0);
    });

    it('should remove notifications', () => {
      const { addNotification, removeNotification } = useNotificationStore.getState();
      
      addNotification({
        type: 'error',
        title: 'Test Error',
        duration: 0,
      });
      
      const notificationId = useNotificationStore.getState().notifications[0].id;
      removeNotification(notificationId);
      
      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
      expect(state.unreadCount).toBe(0);
    });
  });
});