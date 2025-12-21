// المسار: src/features/auth/hooks/useForgotPassword.ts
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

/**
 * دالة الجلب: ترسل البريد الإلكتروني إلى نقطة النهاية الصحيحة.
 */
const requestPasswordReset = async (email: string) => {
  const { data } = await apiClient.post('/api/auth/request-password-reset', { email });
  return data;
};

/**
 * الـ Hook المخصص (Custom Hook) لعملية طلب إعادة التعيين.
 */
export const useForgotPassword = () => {
  return useMutation({
    mutationFn: requestPasswordReset,
    // لا نحتاج لإظهار إشعار نجاح هنا، لأن الواجهة ستتغير لتعرض رسالة
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "فشل إرسال الطلب. تأكد من البريد الإلكتروني.");
    },
  });
};