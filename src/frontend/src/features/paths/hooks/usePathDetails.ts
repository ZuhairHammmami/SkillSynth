// المسار: src/features/paths/hooks/usePathDetails.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

// --- تعريف أنواع البيانات الدقيقة كما وردت من الباك اند ---

// يمثل موردًا تعليميًا واحدًا (رئيسي أو إضافي)
export interface Resource {
  id: number;
  title: string;
  url: string;
  type: string;
  is_free: boolean;
  is_official: boolean;
  author_or_platform: string;
}

// يمثل خطوة واحدة في المسار التعليمي
export interface PathStep {
  id: number;
  path_id: number;
  step_number: number;
  title: string;
  content: string; // الوصف النصي للخطوة
  resources: Resource[]; // قائمة بكل الموارد لهذه الخطوة
}

// يمثل مهارة واحدة يغطيها المسار
export interface Skill {
  id: number;
  name: string;
}

// يمثل الكائن الكامل لتفاصيل المسار
export interface PathDetails {
  id: number;
  profile_id: number;
  title: string;
  description: string; // هذه هي رسالة الترحيب الجديدة
  steps: PathStep[];
  skills: Skill[];
}
// ----------------------------------------------------

/**
 * دالة الجلب (Fetcher): تتصل بالـ API لجلب تفاصيل مسار معين.
 * @param pathId - معرّف المسار المطلوب.
 */
const fetchPathDetails = async (pathId: string): Promise<PathDetails> => {
  const { data } = await apiClient.get<PathDetails>(`/api/paths/${pathId}`);
  return data;
};

/**
 * الـ Hook المخصص (Custom Hook) لجلب وعرض تفاصيل المسار.
 * @param pathId - معرّف المسار الذي سيتم جلبه.
 */
export const usePathDetails = (pathId: string) => {
  return useQuery({
    // المفتاح فريد لكل مسار، مما يسمح بالتخزين المؤقت لكل صفحة على حدة
    queryKey: ['path', pathId],
    queryFn: () => fetchPathDetails(pathId),
    // لا تقم بتشغيل هذا الطلب إلا إذا كان لدينا pathId صالح
    enabled: !!pathId,
    // في حالة الخطأ، لا تقم بإعادة المحاولة تلقائيًا
    retry: false,
  });
};