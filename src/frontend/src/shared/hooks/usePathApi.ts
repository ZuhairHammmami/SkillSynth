'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { queryKeys } from '@/shared/api/query-keys';
import type { Path, GeneratePathInput, DashboardProgress } from '@/types/api';

export function usePaths() {
  return useQuery({
    queryKey: queryKeys.paths.all,
    queryFn: async () => {
      const res = await apiClient.get<Path[]>('/paths/');
      return res.data;
    },
  });
}

export function usePathDetail(id: number) {
  return useQuery({
    queryKey: queryKeys.compat.pathDetail(id),
    queryFn: async () => {
      const res = await apiClient.get<Path>(`/paths/${id}`);
      return res.data;
    },
    enabled: !!id,
    refetchInterval: 10000,
  });
}

export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.compat.dashboard(),
    queryFn: async () => {
      const res = await apiClient.get<DashboardProgress>('/progress/dashboard');
      return res.data;
    },
    refetchInterval: 30000,
  });
}

export function useGeneratePath() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: GeneratePathInput) => {
      const res = await apiClient.post('/generate-path/', input);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.paths.all }),
  });
}

export function useDeletePath() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/paths/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.paths.all }),
  });
}

export function useCompleteStep() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (stepId: number) => {
      const res = await apiClient.post(`/steps/${stepId}/complete`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.compat.pathAll() });
      queryClient.invalidateQueries({ queryKey: queryKeys.compat.dashboard() });
    },
  });
}

export function useUndoCompleteStep() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (stepId: number) => {
      const res = await apiClient.post(`/steps/${stepId}/undo-complete`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.compat.pathAll() });
      queryClient.invalidateQueries({ queryKey: queryKeys.compat.dashboard() });
    },
  });
}
