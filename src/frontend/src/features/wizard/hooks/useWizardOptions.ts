// src/features/wizard/hooks/useWizardOptions.ts
'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { queryKeys } from '@/shared/api/query-keys';
import { useAuthStore } from '@/shared/store/authStore';

export interface WizardPreferences {
  formats: string[];
  languages: string[];
}

export interface WizardOptions {
  job_roles: string[];
  preferences: WizardPreferences;
}

const fetchWizardOptions = async (): Promise<WizardOptions> => {
  const { data } = await apiClient.get<WizardOptions>('/api/wizard-options');
  return data;
};

/**
 * Custom hook to fetch wizard generation options
 * 
 * Returns available options for:
 * - Job roles
 * - Skill levels
 * - Learning styles
 * - Time commitments
 * - Categories
 * 
 * Used in the path generation wizard to populate dropdowns and form fields
 */
export const useWizardOptions = () => {
  // Check authentication status from session store
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return useQuery({
    queryKey: queryKeys.wizard.options(),
    queryFn: fetchWizardOptions,
    enabled: isAuthenticated, // Only fetch if user is authenticated
    staleTime: 1000 * 60 * 30, // 30 minutes - static data changes infrequently
  });
};
