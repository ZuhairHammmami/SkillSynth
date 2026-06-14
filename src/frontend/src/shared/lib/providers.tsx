// src/shared/lib/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ReactNode, useState } from 'react';

/**
 * Create a new QueryClient instance with optimized settings
 * This is called once when the provider mounts
 */
const createQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // 5 minutes - data is considered fresh for this duration
        staleTime: 1000 * 60 * 5,

        // 30 minutes - how long to keep inactive data in cache
        gcTime: 1000 * 60 * 30,

        // Don't refetch when window regains focus
        // This prevents unnecessary requests when switching browser tabs
        refetchOnWindowFocus: false,

        // Automatically retry failed requests once
        retry: 1,

        // Delay retry by 1 second
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
      mutations: {
        // Retry mutations once on failure
        retry: 1,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
    },
  });
};

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Root provider component that wraps the application
 * Provides React Query context and DevTools for debugging
 */
export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(() => createQueryClient());

  const isDevMode = process.env.NODE_ENV === 'development';

  return (
    <QueryClientProvider client={queryClient}>
      {children}

      {/* React Query DevTools - only visible in development */}
      {isDevMode && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition="bottom-right"
          // Uncomment to persist state across page reloads
          // persistQueryClient={{
          //   storage: localStorage,
          // }}
        />
      )}
    </QueryClientProvider>
  );
}