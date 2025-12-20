// المسار: src/features/auth/hooks/useLogin.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

// تعريف شكل البيانات التي نرسلها (Credentials)
interface LoginCredentials {
  email: string;
  password: string;
}

// تعريف شكل الاستجابة التي نتوقعها
interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * دالة الجلب (Mutation Function): تقوم بالعمل الفعلي.
 * ترسل طلب POST إلى نقطة نهاية /api/auth/token.
 */
const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  // الباك اند يتوقع بيانات form-urlencoded هنا
  const params = new URLSearchParams();
  params.append('username', credentials.email);
  params.append('password', credentials.password);
  params.append('grant_type', 'password');

  const response = await apiClient.post<LoginResponse>('/api/auth/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return response.data;
};

/**
 * الـ Hook المخصص (Custom Hook): يغلف `useMutation` ويدير ما يحدث بعد الطلب.
 * `useMutation` مصمم للعمليات التي تغير البيانات في الخادم (POST, PUT, DELETE).
 */
export const useLogin = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      // --- عند النجاح ---
      // 1. ضع التوكن في الكوكيز
      Cookies.set('authToken', data.access_token, { expires: 7 });
      
      // 2. أخبر React Query بأن بيانات 'user' أصبحت قديمة وتحتاج لإعادة جلب
      //    هذا سيقوم تلقائيًا بتشغيل `fetchUser` في `useUser` Hook.
      queryClient.invalidateQueries({ queryKey: ['user'] });
      
      // 3. أظهر إشعار نجاح
      toast.success("مرحباً بعودتك!", { description: "تم تسجيل دخولك بنجاح." });
      
      // 4. وجه المستخدم إلى لوحة التحكم
      router.push('/dashboard');
    },
    onError: (error: any) => {
      // --- عند الفشل ---
      // أظهر إشعار خطأ بالرسالة القادمة من الباك اند
      toast.error(error.response?.data?.detail || 'فشل تسجيل الدخول. تأكد من بياناتك.');
    },
  });
};