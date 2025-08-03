import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UIState } from './types';

export const useUIStore = create<UIState>()(
  persist(
    (set, _) => ({
      // Initial state
      sidebarCollapsed: false,
      theme: 'system',
      modals: {},
      loadingStates: {},

      // Actions
      toggleSidebar: () => {
        set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed,
        }));
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
      },

      setTheme: (theme: 'light' | 'dark' | 'system') => {
        set({ theme });
        
        // Apply theme to document
        const root = document.documentElement;
        if (theme === 'system') {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          root.classList.toggle('dark', prefersDark);
        } else {
          root.classList.toggle('dark', theme === 'dark');
        }
      },

      openModal: (modalId: string) => {
        set((state) => ({
          modals: {
            ...state.modals,
            [modalId]: true,
          },
        }));
      },

      closeModal: (modalId: string) => {
        set((state) => ({
          modals: {
            ...state.modals,
            [modalId]: false,
          },
        }));
      },

      setLoading: (key: string, loading: boolean) => {
        set((state) => ({
          loadingStates: {
            ...state.loadingStates,
            [key]: loading,
          },
        }));
      },
    }),
    {
      name: 'ui-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
        // Don't persist modals and loading states
      }),
    }
  )
);

// Set up system theme change listener
if (typeof window !== 'undefined') {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handleThemeChange = () => {
    const { theme } = useUIStore.getState();
    if (theme === 'system') {
      document.documentElement.classList.toggle('dark', mediaQuery.matches);
    }
  };

  mediaQuery.addEventListener('change', handleThemeChange);
  
  // Apply initial theme
  const { theme } = useUIStore.getState();
  useUIStore.getState().setTheme(theme);
}