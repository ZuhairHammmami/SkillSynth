// المسار: src/features/user/hooks/useChangePassword.ts
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { toast } from 'sonner';

// 1. تعريف شكل البيانات التي سترسلها الدالة إلى الـ API
export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

/**
 * دالة الجلب: تقوم بالعمل الفعلي.
 * الآن تستقبل كائنًا من النوع ChangePasswordData.
 */
const changePassword = async (passwords: ChangePasswordData) => {
   const { data } = await apiClient.post('/api/auth/change-password', passwords);
   return data;
};

/**
 * الـ Hook المخصص (Custom Hook).
 */
export const useChangePassword = () => {
  return useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      toast.success("تم تغيير كلمة المرور بنجاح.");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "فشل تغيير كلمة المرور.");
    },
  });
};