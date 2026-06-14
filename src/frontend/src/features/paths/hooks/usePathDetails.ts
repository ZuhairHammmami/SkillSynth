import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';

export interface Skill {
  id: number;
  name: string;
}

export interface Resource {
  title: string;
  url: string;
  type: string;
}

export interface PathStep {
  id: number;
  step_number: number;
  title: string;
  content: string;
  is_completed?: boolean; // أضفنا علامة الاستفهام
  resources?: Resource[];
  assessments?: any[];
}

export interface PathDetails {
  id: number;
  title: string;
  description: string;
  total_estimated_hours?: number; // أضفنا هذا الحقل
  skills: Skill[];
  steps: PathStep[];
}

export const usePathDetails = (pathId: string) => {
  return useQuery({
    queryKey: ['path-details', pathId],
    queryFn: async () => {
      const { data } = await apiClient.get<PathDetails>(`/api/paths/${pathId}`);
      return data;
    },
    enabled: !!pathId,
  });
};