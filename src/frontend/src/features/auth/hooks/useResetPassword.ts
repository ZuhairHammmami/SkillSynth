import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import apiClient from '@/shared/lib/api';

export interface ResetPasswordData {
  new_password: string;
}

export const useResetPassword = () => {
  return useMutation({
    mutationFn: async ({ new_password }: ResetPasswordData) => {
      const token = new URLSearchParams(window.location.search).get('token');
      if (!token) {
        throw new Error('رابط إعادة التعيين غير صالح. لا يوجد رمز تحقق.');
      }
      const { data } = await apiClient.post('/api/auth/reset-password', {
        token,
        new_password,
      });
      return data;
    },
    onSuccess: () => {
      toast.success("تم إعادة تعيين كلمة المرور بنجاح!", {
        description: "يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة.",
      });
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || error.message || "فشل إعادة التعيين. قد يكون الرابط منتهي الصلاحية.";
      toast.error(message);
    },
  });
};
