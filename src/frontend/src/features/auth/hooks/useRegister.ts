// المسار: src/features/auth/hooks/useRegister.ts
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

// تعريف شكل البيانات التي نرسلها
interface RegisterCredentials {
  email: string;
  full_name: string;
  password: string;
}

/**
 * دالة الجلب (Mutation Function): ترسل طلب POST إلى /api/auth/register.
 */
const register = async (credentials: RegisterCredentials) => {
  const response = await apiClient.post('/api/auth/register', credentials);
  return response.data;
};

/**
 * الـ Hook المخصص (Custom Hook) لعملية إنشاء الحساب.
 */
export const useRegister = () => {
  const router = useRouter();

  return useMutation({
    mutationFn: register,
    onSuccess: () => {
      // --- عند النجاح ---
      // 1. أظهر إشعار نجاح
      toast.success("تم إنشاء حسابك بنجاح!", {
        description: "سيتم الآن توجيهك لصفحة تسجيل الدخول.",
      });
      
      // 2. وجه المستخدم إلى صفحة تسجيل الدخول ليكمل العملية
      router.push('/login');
    },
    onError: (error: any) => {
      // --- عند الفشل ---
      toast.error(error.response?.data?.detail || 'فشل إنشاء الحساب. قد يكون البريد الإلكتروني مستخدمًا.');
    },
  });
};