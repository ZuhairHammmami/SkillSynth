// المسار: src/features/auth/hooks/useResetPassword.ts
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

// تعريف شكل البيانات التي سترسلها الدالة إلى الـ API
export interface ResetPasswordData {
  token: string;
  new_password: string;
}

/**
 * دالة الجلب: تقوم بإرسال التوكن وكلمة المرور الجديدة.
 */
const resetPassword = async (data: ResetPasswordData) => {
   const response = await apiClient.post('/api/auth/reset-password', data);
   return response.data;
};

/**
 * الـ Hook المخصص (Custom Hook) لعملية إعادة التعيين.
 */
export const useResetPassword = () => {
  return useMutation({
    mutationFn: resetPassword,
    onSuccess: () => {
      toast.success("تم إعادة تعيين كلمة المرور بنجاح!", {
        description: "يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة.",
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "فشل إعادة التعيين. قد يكون الرابط منتهي الصلاحية.");
    },
  });
};