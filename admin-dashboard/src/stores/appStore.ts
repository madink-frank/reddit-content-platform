import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppState } from './types';

export const useAppStore = create<AppState>()(
  persist(
    (set, _) => ({
      // Initial state
      isOnline: navigator.onLine,
      lastActivity: Date.now(),
      features: {
        analytics: true,
        notifications: true,
        realTimeUpdates: true,
      },

      // Actions
      setOnlineStatus: (isOnline: boolean) => {
        set({ isOnline });
      },

      updateLastActivity: () => {
        set({ lastActivity: Date.now() });
      },

      toggleFeature: (feature: keyof AppState['features']) => {
        set((state) => ({
          features: {
            ...state.features,
            [feature]: !state.features[feature],
          },
        }));
      },
    }),
    {
      name: 'app-store',
      partialize: (state) => ({
        features: state.features,
        // Don't persist online status and last activity
      }),
    }
  )
);

// Set up online/offline listeners
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    useAppStore.getState().setOnlineStatus(true);
  });

  window.addEventListener('offline', () => {
    useAppStore.getState().setOnlineStatus(false);
  });

  // Update activity on user interactions
  const updateActivity = () => {
    useAppStore.getState().updateLastActivity();
  };

  ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach((event) => {
    document.addEventListener(event, updateActivity, { passive: true });
  });
}