// src/shared/api/usePrefetch.ts
'use client';

import { useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/shared/api/query-keys';

/**
 * usePrefetch - Intelligent prefetching hook for improved perceived performance
 * 
 * Usage:
 * ```tsx
 * const prefetch = usePrefetch();
 * 
 * <div onMouseEnter={() => prefetch.paths()}>
 *   Hover to prefetch paths
 * </div>
 * ```
 * 
 * Performance Impact:
 * - Reduces perceived latency when users navigate
 * - Data is already in cache when user clicks
 * - No network waste - only prefetches if not in cache
 */
export function usePrefetch() {
  const queryClient = useQueryClient();

  /**
   * Prefetch all learning paths for the authenticated user
   * Called when user hovers over dashboard cards or wizard button
   */
  const prefetchPaths = useCallback(async () => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.paths.list(),
      staleTime: 1000 * 60 * 5, // 5 minutes
    });
  }, [queryClient]);

  /**
   * Prefetch a specific path's details
   * Called when user hovers over a path card
   */
  const prefetchPathDetails = useCallback(async (pathId: string) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.paths.detail(pathId),
      staleTime: 1000 * 60 * 5, // 5 minutes
    });
  }, [queryClient]);

  /**
   * Prefetch wizard options
   * Called when user hovers over the "Create New Path" button
   */
  const prefetchWizardOptions = useCallback(async () => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.wizard.options(),
      staleTime: 1000 * 60 * 10, // 10 minutes
    });
  }, [queryClient]);

  /**
   * Prefetch user profile data
   * Called on page load or when user hovers over profile menu
   */
  const prefetchUser = useCallback(async () => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.user.profile(),
      staleTime: 1000 * 60 * 30, // 30 minutes
    });
  }, [queryClient]);

  /**
   * Prefetch multiple paths at once (with IDs)
   * Called when rendering a list to prefetch all upcoming paths
   */
  const prefetchMultiplePaths = useCallback(async (pathIds: string[]) => {
    await Promise.all(
      pathIds.map((id) =>
        queryClient.prefetchQuery({
          queryKey: queryKeys.paths.detail(id),
          staleTime: 1000 * 60 * 5, // 5 minutes
        })
      )
    );
  }, [queryClient]);

  return {
    paths: prefetchPaths,
    pathDetails: prefetchPathDetails,
    wizardOptions: prefetchWizardOptions,
    user: prefetchUser,
    multiplePaths: prefetchMultiplePaths,
  };
}

export default usePrefetch;
