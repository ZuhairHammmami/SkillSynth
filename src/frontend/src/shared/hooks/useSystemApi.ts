'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { queryKeys } from '@/shared/api/query-keys';

export function useWizardOptions() {
  return useQuery({
    queryKey: queryKeys.compat.wizardOptions(),
    queryFn: async () => {
      const res = await apiClient.get('/wizard-options');
      return res.data;
    },
  });
}
