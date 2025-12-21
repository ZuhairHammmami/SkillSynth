// المسار: src/features/auth/hooks/useLogin.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import type { User } from '@/store/authStore';

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
}

// دالة منفصلة لجلب المستخدم، للتأكد من أنها تركز على مهمة واحدة
const fetchUserAfterLogin = async (token: string): Promise<User> => {
    const { data } = await apiClient.get<User>('/api/auth/users/me', {
        headers: { Authorization: `Bearer ${token}` }
    });
    return data;
}

// الدالة الأساسية التي سيتم استدعاؤها من useMutation
const loginAndFetchUser = async (credentials: LoginCredentials): Promise<{token: string, user: User}> => {
  const params = new URLSearchParams();
  params.append('username', credentials.email);
  params.append('password', credentials.password);
  params.append('grant_type', 'password');

  const { data: tokenData } = await apiClient.post<LoginResponse>('/api/auth/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  
  const user = await fetchUserAfterLogin(tokenData.access_token);
  
  return { token: tokenData.access_token, user };
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: loginAndFetchUser,
    onSuccess: (data) => {
      // 1. ضع التوكن في الكوكيز
      Cookies.set('authToken', data.token, { expires: 7 });
      
      // 2. قم بتحديث بيانات 'user' في ذاكرة React Query فورًا وبشكل استباقي
      queryClient.setQueryData(['user'], data.user);
      
      toast.success("مرحباً بعودتك!", { description: "تم تسجيل دخولك بنجاح." });
      
      // --- هذا هو المنطق الحاسم والمصحح ---
      // تحقق من دور المستخدم وقم بإعادة التوجيه إلى الوجهة الصحيحة
      if (data.user.is_admin) {
        router.push('/admin/dashboard');
      } else {
        router.push('/dashboard');
      }
      // ------------------------------------
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'فشل تسجيل الدخول. تأكد من بياناتك.');
    },
  });
};