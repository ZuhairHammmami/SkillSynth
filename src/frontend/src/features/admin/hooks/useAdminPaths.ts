import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';

// تعريف نوع البيانات للمسار كما يأتي من الباك اند
export interface AdminPath {
  id: string | number;
  title: string;
  user_email: string; // سنحتاج لاسم المستخدم أو ايميله
  total_estimated_hours: number;
  created_at: string;
  is_completed: boolean;
}

const fetchAdminPaths = async (): Promise<AdminPath[]> => {
  // ملاحظة: إذا لم يكن هذا الـ Endpoint موجوداً في الباك اند، سيعطي خطأ
  // سنقوم بإصلاح الباك اند في الخطوة التالية
  const { data } = await apiClient.get<AdminPath[]>('/api/admin/paths');
  return data;
};

export const useAdminPaths = () => {
  return useQuery({
    queryKey: ['admin-paths'],
    queryFn: fetchAdminPaths,
  });
};