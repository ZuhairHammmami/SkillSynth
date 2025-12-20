// المسار: src/features/paths/hooks/usePaths.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

// تعريف شكل البيانات المتوقعة من GET /api/paths/
interface LearningPath {
  id: number;
  title: string;
  total_estimated_hours: number;
}

/**
 * دالة الجلب: تقوم بالاتصال بالـ API لجلب قائمة المسارات.
 */
const fetchPaths = async (): Promise<LearningPath[]> => {
  const { data } = await apiClient.get<LearningPath[]>('/api/paths/');
  return data;
};

/**
 * الـ Hook المخصص: يغلف `useQuery` ويوفر طريقة سهلة لجلب المسارات.
 */
export const usePaths = () => {
  return useQuery({
    queryKey: ['paths'], // مفتاح فريد لهذه البيانات في ذاكرة التخزين المؤقت
    queryFn: fetchPaths,
    // يمكننا إضافة إعدادات أخرى هنا، مثل:
    // enabled: !!useAuthStore.getState().user, // لا تقم بالجلب إلا إذا كان المستخدم مسجلاً دخوله
  });
};