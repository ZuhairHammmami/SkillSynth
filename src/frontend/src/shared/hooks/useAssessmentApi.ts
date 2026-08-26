'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';

export interface WizardQuestion {
  id: string;
  skill: string;
  text: string;
  options: string[];
}

export function useRoleQuestions(roleTitle: string | null) {
  return useQuery({
    queryKey: ['roleQuestions', roleTitle],
    queryFn: async () => {
      const res = await apiClient.get<WizardQuestion[]>(
        `/assessments/role/${encodeURIComponent(roleTitle ?? '')}`
      );
      return res.data;
    },
    enabled: !!roleTitle,
    staleTime: 5 * 60 * 1000,
  });
}