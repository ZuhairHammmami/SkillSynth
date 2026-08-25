'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { queryKeys } from '@/shared/api/query-keys';
import type { AnalyticsDashboard } from '@/types/api';

export function useAnalyticsDashboard() {
  return useQuery({
    queryKey: queryKeys.compat.analyticsDashboard(),
    queryFn: async () => {
      const res = await apiClient.get<AnalyticsDashboard>('/analytics/dashboard');
      return res.data;
    },
    refetchInterval: 30000,
  });
}

export function useSkillGrowth() {
  return useQuery({
    queryKey: queryKeys.compat.skillGrowth(),
    queryFn: async () => {
      const res = await apiClient.get('/analytics/skill-growth');
      return res.data;
    },
    refetchInterval: 30000,
  });
}
