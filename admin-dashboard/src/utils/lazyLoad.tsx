import React, { Suspense, ComponentType } from 'react';
import LoadingSpinner from '../components/ui/LoadingSpinner';

interface LazyLoadOptions {
  fallback?: React.ReactNode;
  delay?: number;
}

/**
 * Higher-order component for lazy loading with custom fallback
 */
export function withLazyLoading<T extends {}>(
  importFunc: () => Promise<{ default: ComponentType<T> }>,
  options: LazyLoadOptions = {}
) {
  const { fallback, delay = 0 } = options;

  const LazyComponent = React.lazy(() => {
    if (delay > 0) {
      return new Promise<{ default: ComponentType<T> }>(resolve => {
        setTimeout(() => {
          resolve(importFunc());
        }, delay);
      });
    }
    return importFunc();
  });

  const WrappedComponent: React.FC<T> = (props) => {
    const defaultFallback = (
      <div className="flex items-center justify-center min-h-[200px]">
        <LoadingSpinner size="lg" />
      </div>
    );

    return (
      <Suspense fallback={fallback || defaultFallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };

  WrappedComponent.displayName = `withLazyLoading(Component)`;

  return WrappedComponent;
}

/**
 * Lazy loading wrapper for page components
 */
export function LazyPage({ 
  children, 
  loading = false 
}: { 
  children: React.ReactNode; 
  loading?: boolean; 
}) {
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-gray-500 dark:text-gray-400">Loading page...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

/**
 * Intersection Observer hook for lazy loading content
 */
export function useIntersectionObserver(
  ref: React.RefObject<HTMLElement | null>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = React.useState(false);
  const [hasIntersected, setHasIntersected] = React.useState(false);

  React.useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [ref, hasIntersected, options]);

  return { isIntersecting, hasIntersected };
}

/**
 * Lazy content component that loads when in viewport
 */
export function LazyContent({
  children,
  fallback,
  className = '',
}: {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  className?: string;
}) {
  const ref = React.useRef<HTMLDivElement>(null);
  const { hasIntersected } = useIntersectionObserver(ref);

  const defaultFallback = (
    <div className="flex items-center justify-center py-8">
      <LoadingSpinner size="md" />
    </div>
  );

  return (
    <div ref={ref} className={className}>
      {hasIntersected ? children : (fallback || defaultFallback)}
    </div>
  );
}