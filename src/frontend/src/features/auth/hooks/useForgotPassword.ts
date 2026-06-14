import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import apiClient from '@/shared/lib/api';

export const useForgotPassword = () => {
  return useMutation({
    mutationFn: async (email: string) => {
      const { data } = await apiClient.post('/api/auth/request-password-reset', { email });
      return data;
    },
    onSuccess: () => {
      toast.success("تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || error.message || "فشل إرسال الطلب. تأكد من البريد الإلكتروني.";
      toast.error(message);
    },
  });
};
