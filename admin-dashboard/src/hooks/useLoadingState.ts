import { useUIStore } from '../stores/uiStore';

/**
 * Hook for managing loading states
 */
export const useLoadingState = (key?: string) => {
  const { loadingStates, setLoading } = useUIStore();

  const isLoading = key ? loadingStates[key] || false : false;

  const setLoadingState = (loading: boolean, loadingKey?: string) => {
    const targetKey = loadingKey || key;
    if (targetKey) {
      setLoading(targetKey, loading);
    }
  };

  return {
    isLoading,
    setLoading: setLoadingState,
    loadingStates,
  };
};

/**
 * Hook for managing multiple loading states
 */
export const useLoadingStates = (keys: string[]) => {
  const { loadingStates, setLoading } = useUIStore();

  const getIsLoading = (key: string) => loadingStates[key] || false;
  const isAnyLoading = keys.some((key) => loadingStates[key]);
  const isAllLoading = keys.every((key) => loadingStates[key]);

  return {
    isLoading: getIsLoading,
    isAnyLoading,
    isAllLoading,
    setLoading,
    loadingStates,
  };
};