import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import apiClient from '@/shared/lib/api';

interface RegisterCredentials {
  email: string;
  full_name: string;
  password: string;
}

export const useRegister = () => {
  const router = useRouter();

  return useMutation({
    mutationFn: async (credentials: RegisterCredentials) => {
      const { data } = await apiClient.post('/api/auth/register', credentials);
      return data;
    },
    onSuccess: () => {
      toast.success("تم إنشاء حسابك بنجاح!", {
        description: "سيتم الآن توجيهك لصفحة تسجيل الدخول.",
      });
      router.push('/login');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || error.message || 'فشل إنشاء الحساب. قد يكون البريد الإلكتروني مستخدمًا.';
      toast.error(message);
    },
  });
};
