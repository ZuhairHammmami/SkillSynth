// المسار: src/features/paths/hooks/usePathDetails.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

// تعريف أنواع البيانات المفصلة
interface StepResource { url: string; title: string; }
interface PathStep { id: number; step_number: number; title: string; content: string; }
export interface PathDetails { id: number; title: string; description: string | null; steps: PathStep[]; }

/**
 * دالة الجلب: تأخذ ID المسار وتقوم بجلبه من الـ API.
 */
const fetchPathDetails = async (pathId: string): Promise<PathDetails> => {
  const { data } = await apiClient.get<PathDetails>(`/api/paths/${pathId}`);
  return data;
};

/**
 * الـ Hook المخصص: يأخذ ID المسار كمدخل.
 */
export const usePathDetails = (pathId: string) => {
  return useQuery({
    // المفتاح الآن ديناميكي، ويعتمد على ID المسار
    queryKey: ['path', pathId],
    queryFn: () => fetchPathDetails(pathId),
    // لا تقم بتشغيل هذا الطلب إلا إذا كان لدينا pathId صالح
    enabled: !!pathId,
  });
};