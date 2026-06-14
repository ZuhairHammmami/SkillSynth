// src/features/paths/hooks/usePaths.ts
'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { Path } from '@/entities/path';
import { queryKeys } from '@/shared/api/query-keys';
import { useAuthStore } from '@/shared/store/authStore';

/**
 * Fetches all learning paths for the current user
 */
const fetchPaths = async (): Promise<Path[]> => {
  const { data } = await apiClient.get<Path[]>('/api/paths/');
  return data;
};

/**
 * Custom hook to fetch learning paths
 * 
 * Returns a list of all learning paths available to the current user
 * Automatically disabled if user is not authenticated
 */
export const usePaths = () => {
  // Check authentication status from session store
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return useQuery({
    queryKey: queryKeys.paths.list(),
    queryFn: fetchPaths,
    enabled: isAuthenticated, // Only fetch if user is authenticated
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};